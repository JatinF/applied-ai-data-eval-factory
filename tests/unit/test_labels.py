from __future__ import annotations

import inspect

from data_eval_factory.adjudication.consensus import adjudicate_row
from data_eval_factory.adjudication.disagreement import reviewers_agree
from data_eval_factory.evaluation.metrics import cohen_kappa
from data_eval_factory.schemas.ticket import TicketSignals
from data_eval_factory.weak_supervision.label_model import estimate_accuracies, predict
from data_eval_factory.weak_supervision.labeling_functions import (
    V1_LFS,
    V2_LFS,
    LFContext,
    lf_password_reset,
)


def _signals(**overrides: object) -> TicketSignals:
    payload: dict[str, object] = {
        "id": "ticket-0001",
        "text": "schedule the window",
        "service": "unknown",
        "severity": "P3",
        "error_codes": [],
        "product": "unknown",
        "recorded_type": "",
        "historical_resolution": "",
        "relevant_doc_ids": [],
    }
    payload.update(overrides)
    return TicketSignals.model_validate(payload)


def test_registry_has_the_required_functions() -> None:
    assert len(V1_LFS) >= 10
    assert len(V2_LFS) >= len(V1_LFS) + 3
    assert "gold_type" not in inspect.signature(estimate_accuracies).parameters


def test_password_function_abstains_without_evidence() -> None:
    assert lf_password_reset(_signals(), LFContext(history=())) is None
    labeled = lf_password_reset(
        _signals(text="password rotation failed"),
        LFContext(history=()),
    )
    assert labeled == "ACCOUNT_ACCESS"


def test_label_model_trusts_the_agreeing_function() -> None:
    matrix = [
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, 1],
        [0, 0, -1],
    ]
    accuracies = estimate_accuracies(matrix)
    assert accuracies[0] > accuracies[2]
    labels, _confidence = predict(matrix, accuracies)
    assert labels[0] == "ACCOUNT_ACCESS"


def test_kappa_matches_the_hand_example() -> None:
    assert cohen_kappa(["A", "A", "B", "B"], ["A", "B", "B", "B"]) == 0.5


def test_adjudicator_prefers_http_status_over_service() -> None:
    names = ["lf_billing_keywords", "lf_error_401_403"]
    row = ["PAYMENTS", "AUTHORIZATION"]
    decision = adjudicate_row(_signals(service="payments", error_codes=["403"]), names, row)
    assert reviewers_agree("AUTHORIZATION", "PAYMENTS") is False
    assert decision.agreement is False
    assert decision.adjudicated_label == "AUTHORIZATION"
    assert "401/403" in decision.reason
