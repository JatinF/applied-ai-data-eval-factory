from __future__ import annotations

import json
from pathlib import Path

from data_eval_factory.benchmark.builder import build_benchmark
from data_eval_factory.data.loader import build_tickets, materialize_raw, write_jsonl
from data_eval_factory.data.versioning import canonical_hash
from data_eval_factory.evaluation.runner import Runtime
from data_eval_factory.schemas.evaluation import FactoryReport, SystemScore
from data_eval_factory.synthetic.generator import generate_synthetic


def write_outputs(root: Path, runtime: Runtime) -> None:
    materialize_raw(root)
    tickets = build_tickets()
    synthetic = generate_synthetic(tickets)
    write_jsonl(root / "data" / "synthetic" / "synthetic.jsonl", synthetic)
    dataset_hash = canonical_hash([ticket.model_dump() for ticket in tickets])
    for version, notes in (
        ("v1", ["Held-out test split."]),
        ("v2", ["Same test ids as v1. Training data changed; the scored set did not."]),
    ):
        items, manifest = build_benchmark(tickets, version, dataset_hash, notes)
        write_jsonl(root / "data" / "benchmark" / f"benchmark_{version}.jsonl", items)
        (root / "data" / "benchmark" / f"manifest_{version}.json").write_text(
            json.dumps(manifest.model_dump(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    report = runtime.report
    (root / "data" / "benchmark" / "manifest.json").write_text(
        json.dumps(
            {"versions": [item.model_dump() for item in report.manifests]},
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    payload = report.model_dump()
    (root / "reports").mkdir(parents=True, exist_ok=True)
    (root / "reports" / "baseline_metrics.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (root / "reports" / "weak_supervision.md").write_text(_weak(report), encoding="utf-8")
    (root / "reports" / "failure_analysis.md").write_text(_failures(report), encoding="utf-8")
    (root / "reports" / "benchmark_v1.md").write_text(_benchmark(report, "v1"), encoding="utf-8")
    (root / "reports" / "final_results.md").write_text(_final(report), encoding="utf-8")


def _score_row(score: SystemScore) -> str:
    grounded = "n/a" if score.groundedness is None else f"{score.groundedness:.4f}"
    recall = "n/a" if score.recall_at_5 is None else f"{score.recall_at_5:.4f}"
    unsafe = "n/a" if score.unsafe_action_rate is None else f"{score.unsafe_action_rate:.4f}"
    return (
        f"| {score.name} | {score.accuracy:.4f} | {score.f1_macro:.4f} | {grounded} | "
        f"{recall} | {score.p50_ms:.4f} | {score.p95_ms:.4f} | {unsafe} |"
    )


def _weak(report: FactoryReport) -> str:
    lines = [
        "# Weak supervision",
        "",
        f"Backend: `{report.label_model_backend}`. Gold labels were not used to fit the model.",
        "",
    ]
    for block in (report.v1, report.v2):
        labeling = block.labeling
        lines.append(f"## {block.iteration}")
        lines.append("")
        lines.append(
            f"Coverage {labeling.coverage:.4f}, overlap {labeling.overlap:.4f}, "
            f"conflict {labeling.conflict:.4f}."
        )
        lines.append("")
        lines.append(
            "| Labeling function | Coverage | Abstention | Estimated accuracy | Gold accuracy |"
        )
        lines.append("| --- | ---: | ---: | ---: | ---: |")
        for function in labeling.labeling_functions:
            gold = "n/a" if function.gold_accuracy is None else f"{function.gold_accuracy:.4f}"
            lines.append(
                f"| {function.name} | {function.coverage:.4f} | {function.abstention_rate:.4f} | "
                f"{function.estimated_accuracy:.4f} | {gold} |"
            )
        lines.append("")
    return "\n".join(lines)


def _failures(report: FactoryReport) -> str:
    lines = [
        "# Failure analysis",
        "",
        "V1 shares use baseline_ml predictions on the test split.",
        "V2 shares use linear_finetune predictions on the same test ids.",
        "",
    ]
    for block in (report.v1, report.v2):
        lines.append(f"## {block.iteration}")
        lines.append("")
        lines.append(f"Failed tickets: {block.failed_tickets}.")
        lines.append("")
        for failure in block.failures:
            lines.append(f"- {failure.failure}: {failure.count} ({failure.share:.4f})")
        lines.append("")
        lines.append("| Slice | Support | Accuracy |")
        lines.append("| --- | ---: | ---: |")
        for slice_score in block.slices:
            lines.append(
                f"| {slice_score.slice} | {slice_score.support} | {slice_score.accuracy:.4f} |"
            )
        lines.append("")
    return "\n".join(lines)


def _benchmark(report: FactoryReport, version: str) -> str:
    manifest = next(item for item in report.manifests if item.version == version)
    lines = [
        f"# Benchmark {version}",
        "",
        f"Items: {manifest.item_count}. Dataset sha256 `{manifest.dataset_sha256}`.",
        "",
        "## Tasks",
        "",
    ]
    lines.extend(f"- {name}: {count}" for name, count in manifest.task_counts.items())
    lines.extend(["", "## Difficulty", ""])
    lines.extend(f"- {name}: {count}" for name, count in manifest.difficulty_counts.items())
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- {note}" for note in manifest.notes)
    lines.append("")
    return "\n".join(lines)


def _final(report: FactoryReport) -> str:
    lines = [
        "# Measured results",
        "",
        "These figures come from `data-eval run` on the synthetic enterprise support set.",
        "No hosted model was called. LoRA was not trained. No price is applied.",
        "",
        f"Tickets {report.ticket_count}. Test {report.test_count}. "
        f"Agreement {report.agreement_rate:.4f}. Cohen's kappa {report.cohen_kappa:.4f}. "
        f"Adjudicated disagreements {report.adjudicated_count}.",
        "",
        f"Synthetic generated {report.synthetic_generated}, approved {report.synthetic_accepted}, "
        f"rejected {report.synthetic_rejected}, mean novelty {report.mean_novelty:.4f}.",
        "",
        "Train and test ids overlap: "
        f"{report.id_overlap}. Max train/test token Jaccard: {report.max_train_test_jaccard:.4f}.",
        "",
        "| System | Accuracy | F1 | Groundedness | Recall@5 | P50 ms | P95 ms | Unsafe |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for block in (report.v1, report.v2):
        lines.append(f"| iteration {block.iteration} | | | | | | | |")
        lines.extend(_score_row(score) for score in block.scores)
    lines.extend(["", "## Curation", ""])
    lines.extend(f"- {note}" for note in report.curation_notes)
    lines.append("")
    return "\n".join(lines)
