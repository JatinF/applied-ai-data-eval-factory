from __future__ import annotations

import time
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import yaml

from data_eval_factory.adjudication.consensus import adjudicate_row
from data_eval_factory.agents.graph import run_agent
from data_eval_factory.agents.policy import is_unsafe
from data_eval_factory.analysis.failures import failure_shares, primary_failure
from data_eval_factory.analysis.slices import slice_accuracy
from data_eval_factory.benchmark.builder import build_benchmark
from data_eval_factory.benchmark.contamination import contamination
from data_eval_factory.data.loader import build_documents, build_tickets, repo_root
from data_eval_factory.data.profiler import profile_tickets
from data_eval_factory.data.versioning import canonical_hash
from data_eval_factory.evaluation.cost_latency import latency_summary
from data_eval_factory.evaluation.groundedness import groundedness, mean_defined
from data_eval_factory.evaluation.judge import arguments_match, citation_correct
from data_eval_factory.evaluation.metrics import accuracy, cohen_kappa, macro_scores
from data_eval_factory.evaluation.retrieval_metrics import ndcg_at_k, recall_at_k, reciprocal_rank
from data_eval_factory.models.baseline import BaselineClassifier
from data_eval_factory.models.finetune import LinearFineTune
from data_eval_factory.models.prompt_model import answer_prompt, classify_prompt
from data_eval_factory.models.rag import answer_retrieved, classify_retrieved
from data_eval_factory.retrieval.index import SearchIndex
from data_eval_factory.retrieval.retriever import Hit, search
from data_eval_factory.schemas.evaluation import (
    FactoryReport,
    IterationReport,
    SliceScore,
    SystemScore,
)
from data_eval_factory.schemas.label import Adjudication
from data_eval_factory.schemas.ticket import Document, Ticket, TicketSignals
from data_eval_factory.synthetic.generator import generate_synthetic
from data_eval_factory.synthetic.quality import review
from data_eval_factory.weak_supervision.analysis import analyze_labels
from data_eval_factory.weak_supervision.apply_labels import label_matrix
from data_eval_factory.weak_supervision.label_model import BACKEND, estimate_accuracies, predict
from data_eval_factory.weak_supervision.labeling_functions import V1_LFS, V2_LFS, apply_functions

PredictFn = Callable[[Ticket, list[Hit]], str | None]
HitFn = Callable[[Ticket], list[Hit]]


@dataclass
class Runtime:
    report: FactoryReport
    baseline: BaselineClassifier
    linear: LinearFineTune
    index: SearchIndex
    documents: list[Document]


def run_factory(root: Path | None = None) -> FactoryReport:
    return execute(root).report


def execute(root: Path | None = None) -> Runtime:
    root = root or repo_root()
    tickets = build_tickets()
    documents = build_documents()
    profile = profile_tickets(tickets)
    dataset_hash = canonical_hash([ticket.model_dump() for ticket in tickets])
    test = [ticket for ticket in tickets if ticket.split == "test"]
    index = SearchIndex.build(documents)
    doc_text = {document.id: document.text for document in documents}

    names_v1, matrix_v1 = label_matrix(tickets, V1_LFS)
    names_v2, matrix_v2 = label_matrix(tickets, V2_LFS)
    labeling_v1 = analyze_labels(tickets, names_v1, matrix_v1)
    labeling_v2 = analyze_labels(tickets, names_v2, matrix_v2)
    weak_labels, _confidence = predict(matrix_v1, estimate_accuracies(matrix_v1))
    decisions = _adjudications(tickets, names_v2)
    synthetic = generate_synthetic(tickets)

    baseline = BaselineClassifier()
    train_pairs = [
        (ticket.text, label)
        for ticket, label in zip(tickets, weak_labels, strict=True)
        if ticket.split == "train" and label
    ]
    baseline.fit(
        [text for text, _label in train_pairs],
        [label for _text, label in train_pairs],
    )
    linear_rows: list[tuple[str, str, tuple[str, ...]]] = []
    linear_labels: list[str] = []
    for ticket, decision, weak in zip(tickets, decisions, weak_labels, strict=True):
        if ticket.split != "train" or ticket.product == "unknown":
            continue
        label = _training_label(decision, weak)
        if label is None:
            continue
        linear_rows.append((ticket.text, ticket.service, tuple(ticket.error_codes)))
        linear_labels.append(label)
    for record in synthetic:
        if record.review_status == "approved":
            linear_rows.append((record.text, record.service, tuple(record.error_codes)))
            linear_labels.append(record.gold_type)
    linear = LinearFineTune()
    linear.fit(linear_rows, linear_labels)

    def hits_for(ticket: Ticket) -> list[Hit]:
        return search(index, ticket.text, k=5)

    def baseline_label(ticket: Ticket, _hits: list[Hit]) -> str | None:
        label, _conf = baseline.predict(ticket.text)
        return label

    def linear_label(ticket: Ticket, _hits: list[Hit]) -> str | None:
        label, _conf = linear.predict(ticket.text, ticket.service, ticket.error_codes)
        return label

    def prompt_v1(ticket: Ticket, _hits: list[Hit]) -> str | None:
        return classify_prompt(ticket.text, strip_appendix=False)

    def prompt_v2(ticket: Ticket, _hits: list[Hit]) -> str | None:
        return classify_prompt(ticket.text, strip_appendix=True)

    def rag_label(ticket: Ticket, hits: list[Hit]) -> str | None:
        return classify_retrieved(hits if hits else hits_for(ticket))

    v1_scores, v1_failures, v1_slices = _evaluate(
        test,
        doc_text,
        hits_for,
        {
            "baseline_ml": (baseline_label, None, False),
            "prompt_template": (prompt_v1, "v1", True),
            "rag_extractive": (rag_label, "rag", True),
            "unguarded_agent": (baseline_label, None, True),
        },
        guarded=False,
        iteration="v1",
        failure_model="baseline_ml",
    )
    v2_scores, _v2_failures, v2_slices = _evaluate(
        test,
        doc_text,
        hits_for,
        {
            "linear_finetune": (linear_label, None, False),
            "prompt_template": (prompt_v2, "v2", True),
            "rag_extractive": (rag_label, "rag", True),
            "guarded_agent": (linear_label, None, True),
        },
        guarded=True,
        iteration="v2",
        failure_model="linear_finetune",
    )
    both_voted = [
        (row.reviewer_a, row.reviewer_b) for row in decisions if row.reviewer_a and row.reviewer_b
    ]
    disagreements = [row for row in decisions if not row.agreement]
    source_text = {ticket.id: ticket.text for ticket in tickets}
    novelties = [
        review(source_text[record.source_id], record.text, record.generation_strategy)[1]
        for record in synthetic
    ]
    accepted = sum(record.review_status == "approved" for record in synthetic)
    rejected = sum(record.review_status == "rejected" for record in synthetic)
    overlap, max_jaccard = contamination(tickets)
    settings = _model_settings(root)
    notes = [
        "Added "
        + str(
            sum(
                item.generation_strategy == "hard_negative" and item.review_status == "approved"
                for item in synthetic
            )
        )
        + " approved hard negatives.",
        "Added labeling functions lf_db_error_code, lf_pay_error_code, and lf_auth_on_payments.",
        "V2 prompt drops the unsupported restart sentence and ignores the glossary appendix.",
        "V2 agent blocks credential reset unless the prediction is account access on the identity "
        "service.",
        "V2 linear model skips context-free rows, keeps weak labels unless an error code overrides "
        "them, and adds approved synthetic rows.",
        "Retrieval documents are unchanged between V1 and V2.",
        "Reviewers are programmed policies, not external people.",
    ]
    v1_items, v1_manifest = build_benchmark(tickets, "v1", dataset_hash, ["Held-out test split."])
    _v2_items, v2_manifest = build_benchmark(
        tickets,
        "v2",
        dataset_hash,
        ["Same test ids as v1. Training data changed; the scored set did not."],
    )
    del v1_items
    report = FactoryReport(
        dataset_sha256=dataset_hash,
        ticket_count=len(tickets),
        document_count=len(documents),
        train_count=sum(ticket.split == "train" for ticket in tickets),
        validation_count=sum(ticket.split == "validation" for ticket in tickets),
        test_count=len(test),
        class_counts=cast(dict[str, int], profile["class_counts"]),
        agreement_rate=(
            sum(row.agreement for row in decisions) / len(decisions) if decisions else 0.0
        ),
        cohen_kappa=cohen_kappa(
            [item[0] for item in both_voted],
            [item[1] for item in both_voted],
        ),
        adjudicated_count=sum(
            1 for row in disagreements if row.adjudicated_label != "ABSTAIN"
        ),
        disagreements_by_label=dict(
            sorted(Counter(row.adjudicated_label for row in disagreements).items())
        ),
        adjudication_examples=disagreements[:5],
        synthetic_generated=len(synthetic),
        synthetic_accepted=accepted,
        synthetic_rejected=rejected,
        synthetic_by_strategy=dict(
            sorted(Counter(record.generation_strategy for record in synthetic).items())
        ),
        duplicate_rate=rejected / len(synthetic) if synthetic else 0.0,
        mean_novelty=sum(novelties) / len(novelties) if novelties else 0.0,
        id_overlap=overlap,
        max_train_test_jaccard=max_jaccard,
        hosted_llm=str(settings.get("hosted_llm", "not-run")),
        lora=str(settings.get("lora", "not-run")),
        label_model_backend=BACKEND,
        v1=IterationReport(
            iteration="v1",
            labeling=labeling_v1,
            scores=v1_scores,
            slices=v1_slices,
            failures=failure_shares(v1_failures),
            failed_tickets=len(v1_failures),
        ),
        v2=IterationReport(
            iteration="v2",
            labeling=labeling_v2,
            scores=v2_scores,
            slices=v2_slices,
            failures=failure_shares(_v2_failures),
            failed_tickets=len(_v2_failures),
        ),
        manifests=[v1_manifest, v2_manifest],
        curation_notes=notes,
    )
    return Runtime(
        report=report,
        baseline=baseline,
        linear=linear,
        index=index,
        documents=documents,
    )


def _training_label(decision: Adjudication, weak: str | None) -> str | None:
    """Keep a confident weak label unless an error code overrides it."""
    reason = decision.reason
    code_override = "outranks" in reason
    payment_override = "identifies the payment" in reason
    authoritative = code_override or payment_override
    if authoritative and decision.adjudicated_label != "ABSTAIN":
        return decision.adjudicated_label
    if weak:
        return weak
    if decision.adjudicated_label != "ABSTAIN":
        return decision.adjudicated_label
    return None


def _adjudications(tickets: list[Ticket], names: list[str]) -> list[Adjudication]:
    history = [
        TicketSignals.from_ticket(ticket) for ticket in tickets if ticket.split == "train"
    ]
    signals = [TicketSignals.from_ticket(ticket) for ticket in tickets]
    raw = apply_functions(signals, V2_LFS, history)
    if [item.name for item in V2_LFS] != names:
        raise RuntimeError("label function order drifted")
    return [
        adjudicate_row(row_signals, names, row)
        for row_signals, row in zip(signals, raw, strict=True)
    ]


def _model_settings(root: Path) -> dict[str, object]:
    path = root / "configs" / "models.yaml"
    if not path.exists():
        return {"hosted_llm": "not-run", "lora": "not-run"}
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        return {"hosted_llm": "not-run", "lora": "not-run"}
    return loaded


def _evaluate(
    test: list[Ticket],
    doc_text: dict[str, str],
    hits_for: HitFn,
    systems: dict[str, tuple[PredictFn, str | None, bool]],
    *,
    guarded: bool,
    iteration: str,
    failure_model: str,
) -> tuple[list[SystemScore], list[str], list[SliceScore]]:
    scores: list[SystemScore] = []
    failure_labels: list[str] = []
    slice_source: tuple[list[Ticket], list[str | None]] | None = None
    for name, (predictor, answer_mode, retrieve) in systems.items():
        truth: list[str] = []
        predicted: list[str | None] = []
        grounded_values: list[float | None] = []
        citation_values: list[float] = []
        recalls: list[float] = []
        mrrs: list[float] = []
        ndcgs: list[float] = []
        tool_hits: list[bool] = []
        arg_hits: list[bool] = []
        completions: list[bool] = []
        unsafe_flags: list[bool] = []
        abstained: list[bool] = []
        appropriate_flags: list[bool] = []
        times: list[float] = []
        use_retrieval = retrieve or answer_mode is not None
        for ticket in test:
            started = time.perf_counter()
            hits = hits_for(ticket) if use_retrieval else []
            label = predictor(ticket, hits)
            answer, cites = _answer(answer_mode, hits)
            action = run_agent(ticket, label, guarded=guarded) if name.endswith("agent") else None
            times.append((time.perf_counter() - started) * 1000)
            truth.append(ticket.gold_type)
            predicted.append(label)
            if answer_mode is not None:
                cited_blob = " ".join(doc_text[doc_id] for doc_id in cites if doc_id in doc_text)
                grounded_values.append(groundedness(answer, cited_blob))
                citation_values.append(
                    citation_correct(cites, ticket.relevant_doc_ids, answer, cited_blob)
                )
            if use_retrieval:
                ranked = [hit.document.id for hit in hits]
                recalls.append(recall_at_k(ranked, ticket.relevant_doc_ids, 5))
                mrrs.append(reciprocal_rank(ranked, ticket.relevant_doc_ids))
                ndcgs.append(ndcg_at_k(ranked, ticket.relevant_doc_ids, 5))
            if action is not None:
                tool_hits.append(action.tool == ticket.gold_tool)
                arg_hits.append(
                    arguments_match(
                        action.tool,
                        action.arguments,
                        ticket.product,
                        ticket.service,
                        ticket.severity,
                    )
                )
                completions.append(tool_hits[-1] and arg_hits[-1])
                unsafe_flags.append(is_unsafe(action, ticket.gold_type))
                abstained.append(action.abstained)
            else:
                abstained.append(label is None)
            if "missing-context" in ticket.slices:
                appropriate_flags.append(action.abstained if action is not None else label is None)
            if name == failure_model:
                if use_retrieval:
                    ranked_ids = [hit.document.id for hit in hits]
                else:
                    ranked_ids = [hit.document.id for hit in hits_for(ticket)]
                if action is not None:
                    tool_name = action.tool
                else:
                    tool_name = run_agent(ticket, label, guarded=guarded).tool
                failure = primary_failure(ticket, label, ranked_ids, tool_name)
                if failure:
                    failure_labels.append(failure)
        if name == failure_model:
            slice_source = (test, predicted)
        precision, recall, f1 = macro_scores(truth, predicted)
        p50, p95 = latency_summary(times)
        scores.append(
            SystemScore(
                name=name,
                iteration=iteration,
                accuracy=accuracy(truth, predicted),
                precision_macro=precision,
                recall_macro=recall,
                f1_macro=f1,
                groundedness=mean_defined(grounded_values) if answer_mode else None,
                citation_correctness=(
                    sum(citation_values) / len(citation_values) if citation_values else None
                ),
                recall_at_5=(sum(recalls) / len(recalls)) if recalls else None,
                mrr=(sum(mrrs) / len(mrrs)) if mrrs else None,
                ndcg_at_5=(sum(ndcgs) / len(ndcgs)) if ndcgs else None,
                tool_selection=(sum(tool_hits) / len(tool_hits)) if tool_hits else None,
                argument_correctness=(sum(arg_hits) / len(arg_hits)) if arg_hits else None,
                task_completion=(sum(completions) / len(completions)) if completions else None,
                unsafe_action_rate=(
                    sum(unsafe_flags) / len(unsafe_flags) if unsafe_flags else None
                ),
                abstention_rate=(sum(abstained) / len(abstained)) if abstained else None,
                appropriate_abstention=(
                    sum(appropriate_flags) / len(appropriate_flags) if appropriate_flags else None
                ),
                p50_ms=p50,
                p95_ms=p95,
            )
        )
    slices = slice_accuracy(*(slice_source or (test, [None] * len(test))))
    return scores, failure_labels, slices


def _answer(mode: str | None, hits: list[Hit]) -> tuple[str | None, list[str]]:
    if mode == "v1":
        return answer_prompt(hits, strip_unsupported=False)
    if mode == "v2":
        return answer_prompt(hits, strip_unsupported=True)
    if mode == "rag":
        return answer_retrieved(hits)
    return None, []
