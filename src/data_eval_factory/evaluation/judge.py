"""Deterministic rubric checks. This is not a hosted judge model."""

from __future__ import annotations


def citation_correct(
    cited_ids: list[str],
    relevant_ids: list[str],
    answer: str | None,
    cited_text: str,
) -> float:
    if answer is None:
        return 0.0
    if not cited_ids or not set(cited_ids) & set(relevant_ids):
        return 0.0
    sentence = answer.split(".", maxsplit=1)[0].strip()
    return 1.0 if sentence and sentence in cited_text else 0.0


def arguments_match(
    tool: str,
    arguments: dict[str, str],
    product: str,
    service: str,
    severity: str,
) -> bool:
    if tool == "abstain":
        return True
    if tool == "reset_credentials":
        return arguments.get("product") == product
    if tool == "restart_service":
        return arguments.get("service") == service
    if tool == "page_oncall":
        return arguments.get("severity") == severity
    if tool == "lookup_runbook":
        return arguments.get("product") == product
    return False
