from __future__ import annotations

import json
from pathlib import Path

from data_eval_factory.analysis.regressions import regression_messages
from data_eval_factory.data.loader import repo_root
from data_eval_factory.schemas.evaluation import FactoryReport


def test_committed_baseline_matches_this_run(report: FactoryReport) -> None:
    path = repo_root() / "reports" / "baseline_metrics.json"
    saved = FactoryReport.model_validate(json.loads(path.read_text(encoding="utf-8")))
    assert regression_messages(report, saved, max_f1_drop=0.02, max_groundedness_drop=0.03) == []
    assert Path(path).exists()
