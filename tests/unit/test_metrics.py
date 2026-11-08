from __future__ import annotations

from data_eval_factory.agents.policy import choose_action, is_unsafe
from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.data.loader import build_tickets
from data_eval_factory.evaluation.groundedness import groundedness
from data_eval_factory.evaluation.metrics import macro_scores
from data_eval_factory.evaluation.retrieval_metrics import ndcg_at_k, recall_at_k, reciprocal_rank
from data_eval_factory.synthetic.generator import generate_synthetic


def test_macro_f1_is_one_when_every_class_is_correct() -> None:
    truth = list(LABELS)
    _precision, _recall, f1 = macro_scores(truth, truth)
    assert f1 == 1


def test_retrieval_metrics_for_a_hit_at_rank_one() -> None:
    ranked = ["runbook-database", "other"]
    relevant = ["runbook-database"]
    assert recall_at_k(ranked, relevant, 5) == 1
    assert reciprocal_rank(ranked, relevant) == 1
    assert ndcg_at_k(ranked, relevant, 5) == 1


def test_groundedness_splits_supported_and_unsupported_sentences() -> None:
    score = groundedness(
        "Password rotation runbook. Restart every production service to be safe",
        "Password rotation runbook. Reset the password.",
    )
    assert score == 0.5


def test_guard_blocks_a_password_reset_outside_account_access() -> None:
    action = choose_action(
        text="password rotation appeared in a pasted glossary",
        predicted="DATABASE",
        service="database",
        severity="P2",
        product="warehouse-db",
        guarded=True,
    )
    assert action.tool != "reset_credentials"
    unsafe = choose_action(
        text="password rotation appeared in a pasted glossary",
        predicted="DATABASE",
        service="database",
        severity="P2",
        product="warehouse-db",
        guarded=False,
    )
    assert is_unsafe(unsafe, "DATABASE")


def test_synthetic_records_keep_provenance() -> None:
    records = [
        record
        for record in generate_synthetic(build_tickets())
        if record.generation_strategy == "hard_negative"
    ]
    assert records
    sample = records[0]
    assert sample.id.startswith("syn-")
    assert sample.generator == "deterministic-template"
    assert sample.prompt_version == "template-v1"
    assert sample.review_status == "approved"
    assert sample.source_id.startswith("ticket-")
