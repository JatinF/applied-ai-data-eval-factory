from __future__ import annotations

from data_eval_factory.schemas.evaluation import FailureShare
from data_eval_factory.schemas.ticket import Ticket


def primary_failure(
    ticket: Ticket,
    predicted: str | None,
    ranked_ids: list[str],
    tool: str,
) -> str | None:
    class_wrong = predicted != ticket.gold_type
    tool_wrong = tool != ticket.gold_tool
    if not class_wrong and not tool_wrong:
        return None
    retrieved = ranked_ids[:5]
    missed = not any(doc_id in retrieved for doc_id in ticket.relevant_doc_ids)
    if class_wrong and "missing-context" in ticket.slices:
        return "insufficient_context"
    if class_wrong and missed:
        return "retrieval_miss"
    if class_wrong and ("ambiguous-tickets" in ticket.slices or "cross-domain" in ticket.slices):
        return "reasoning_error"
    if class_wrong:
        return "classification_error"
    if tool_wrong:
        return "tool_selection"
    return "other"


def failure_shares(labels: list[str]) -> list[FailureShare]:
    names = (
        "retrieval_miss",
        "classification_error",
        "insufficient_context",
        "reasoning_error",
        "tool_selection",
        "other",
    )
    total = len(labels) or 1
    return [
        FailureShare(
            failure=name,
            count=labels.count(name),
            share=labels.count(name) / total,
        )
        for name in names
    ]
