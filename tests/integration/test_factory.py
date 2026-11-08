from __future__ import annotations

from data_eval_factory.benchmark.taxonomy import TAXONOMY
from data_eval_factory.schemas.evaluation import FactoryReport


def test_factory_report_is_complete(report: FactoryReport) -> None:
    assert report.ticket_count > 200
    assert report.test_count > 20
    assert report.id_overlap == 0
    assert report.hosted_llm == "not-run"
    assert report.lora == "not-run"
    assert report.v1.labeling.used_gold_to_fit is False
    assert report.v1.labeling.conflict > 0
    assert len(report.v1.labeling.lf_names) >= 10
    assert report.adjudicated_count > 0
    assert report.cohen_kappa > 0
    assert report.synthetic_accepted > 0
    assert {item.version for item in report.manifests} == {"v1", "v2"}
    tasks = report.manifests[0].task_counts
    for family in TAXONOMY:
        assert tasks[family] > 0
    names = {score.name for score in report.v1.scores}
    assert {"baseline_ml", "prompt_template", "rag_extractive", "unguarded_agent"} <= names
    refined = {score.name for score in report.v2.scores}
    assert "linear_finetune" in refined
    assert "guarded_agent" in refined


def test_refinement_does_not_increase_unsafe_actions(report: FactoryReport) -> None:
    before = next(
        score.unsafe_action_rate for score in report.v1.scores if score.name == "unguarded_agent"
    )
    after = next(
        score.unsafe_action_rate for score in report.v2.scores if score.name == "guarded_agent"
    )
    assert before is not None and after is not None
    assert after <= before
