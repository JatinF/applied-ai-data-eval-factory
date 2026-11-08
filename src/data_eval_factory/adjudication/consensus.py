from __future__ import annotations

from data_eval_factory.adjudication.disagreement import reviewers_agree
from data_eval_factory.adjudication.reviewer import reviewer_a, reviewer_b
from data_eval_factory.schemas.label import Adjudication
from data_eval_factory.schemas.ticket import TicketSignals


def adjudicate_row(
    signals: TicketSignals,
    names: list[str],
    row: list[str | None],
) -> Adjudication:
    left = reviewer_a(names, row)
    right = reviewer_b(signals, names, row)
    codes = set(signals.error_codes)
    if reviewers_agree(left, right) and left is not None:
        label = left
        reason = "reviewers agreed"
    elif codes & {"401", "403"}:
        label = "AUTHORIZATION"
        reason = "HTTP 401/403 outranks service metadata"
    elif "DB-57014" in codes:
        label = "DATABASE"
        reason = "Database error code outranks timeout wording"
    elif "PAY-1102" in codes:
        label = "PAYMENTS"
        reason = "Ledger error code identifies the payment fault"
    elif left is not None:
        label = left
        reason = "keyword reviewer supplied the only class vote"
    elif right is not None:
        label = right
        reason = "metadata reviewer supplied the only class vote"
    else:
        label = "ABSTAIN"
        reason = "insufficient evidence for a class vote"
    return Adjudication(
        sample_id=signals.id,
        reviewer_a=left,
        reviewer_b=right,
        agreement=reviewers_agree(left, right),
        adjudicated_label=label,
        reason=reason,
    )
