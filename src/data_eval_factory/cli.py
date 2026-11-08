from __future__ import annotations

import argparse
import json

import uvicorn

from data_eval_factory.analysis.regressions import regression_messages
from data_eval_factory.data.loader import repo_root
from data_eval_factory.evaluation.reports import write_outputs
from data_eval_factory.evaluation.runner import execute
from data_eval_factory.log import configure_logging
from data_eval_factory.schemas.evaluation import FactoryReport, SystemScore


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="data-eval")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("run")
    serve = sub.add_parser("serve")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    sub.add_parser("check-regression")
    args = parser.parse_args(argv)
    configure_logging()
    root = repo_root()
    if args.command == "run":
        runtime = execute(root)
        write_outputs(root, runtime)
        report = runtime.report
        baseline = _score(report, "v1", "baseline_ml")
        refined = _score(report, "v2", "linear_finetune")
        print(
            f"test={report.test_count} v1_f1={baseline.f1_macro:.4f} v2_f1={refined.f1_macro:.4f} "
            f"kappa={report.cohen_kappa:.4f}"
        )
        return
    if args.command == "serve":
        uvicorn.run(
            "data_eval_factory.api.app:create_app",
            factory=True,
            host=args.host,
            port=args.port,
        )
        return
    current = execute(root).report
    baseline_path = root / "reports" / "baseline_metrics.json"
    saved = FactoryReport.model_validate(json.loads(baseline_path.read_text(encoding="utf-8")))
    messages = regression_messages(current, saved, max_f1_drop=0.02, max_groundedness_drop=0.03)
    report_path = root / "reports" / "regression_report.json"
    report_path.write_text(
        json.dumps({"status": "failed" if messages else "passed", "messages": messages}, indent=2)
        + "\n",
        encoding="utf-8",
    )
    if messages:
        raise SystemExit("\n".join(messages))
    print("regression check passed")


def _score(report: FactoryReport, iteration: str, name: str) -> SystemScore:
    block = report.v2 if iteration == "v2" else report.v1
    for score in block.scores:
        if score.name == name:
            return score
    raise KeyError(name)


if __name__ == "__main__":
    main()
