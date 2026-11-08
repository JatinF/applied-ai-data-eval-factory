from __future__ import annotations

import json
from pathlib import Path

import pytest

from data_eval_factory.cli import main
from data_eval_factory.log import JsonFormatter, configure_logging
from data_eval_factory.schemas.label import Adjudication


def test_unknown_command_exits() -> None:
    with pytest.raises(SystemExit):
        main(["missing"])


def test_json_formatter_emits_level() -> None:
    import logging

    configure_logging()
    record = logging.LogRecord("data_eval_factory", logging.INFO, __file__, 1, "ready", (), None)
    payload = json.loads(JsonFormatter().format(record))
    assert payload["level"] == "INFO"
    assert payload["message"] == "ready"


def test_adjudication_fixture_matches_the_schema() -> None:
    path = Path(__file__).parents[1] / "fixtures" / "adjudication.json"
    row = Adjudication.model_validate(json.loads(path.read_text(encoding="utf-8")))
    assert row.agreement is False
    assert row.adjudicated_label == "DATABASE"
