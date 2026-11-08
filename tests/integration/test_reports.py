from __future__ import annotations

import json
from pathlib import Path

from data_eval_factory.cli import _score
from data_eval_factory.evaluation.reports import write_outputs
from data_eval_factory.evaluation.runner import Runtime
from data_eval_factory.schemas.evaluation import FactoryReport


def test_score_lookup(report: FactoryReport) -> None:
    score = _score(report, "v2", "linear_finetune")
    assert score.iteration == "v2"
    assert score.tokens == 0
    assert score.estimated_cost is None


def test_write_outputs_writes_manifest(runtime: Runtime, tmp_path: Path) -> None:
    write_outputs(tmp_path, runtime)
    raw = (tmp_path / "data" / "benchmark" / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(raw)
    versions = {item["version"] for item in manifest["versions"]}
    assert versions == {"v1", "v2"}
    assert (tmp_path / "reports" / "final_results.md").exists()
    assert (tmp_path / "data" / "synthetic" / "synthetic.jsonl").exists()
