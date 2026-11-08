from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    tool: str
    arguments: dict[str, str]
    abstained: bool


def reset_credentials(product: str) -> Action:
    return Action("reset_credentials", {"product": product}, False)


def restart_service(service: str) -> Action:
    return Action("restart_service", {"service": service}, False)


def page_oncall(severity: str) -> Action:
    return Action("page_oncall", {"severity": severity}, False)


def lookup_runbook(product: str) -> Action:
    return Action("lookup_runbook", {"product": product}, False)


def abstain() -> Action:
    return Action("abstain", {}, True)
