"""Explicit action policy. This module does not use a graph-framework runtime."""

from __future__ import annotations

from data_eval_factory.agents.policy import choose_action
from data_eval_factory.agents.tools import Action
from data_eval_factory.schemas.ticket import Ticket


def run_agent(ticket: Ticket, predicted: str | None, *, guarded: bool) -> Action:
    return choose_action(
        text=ticket.text,
        predicted=predicted,
        service=ticket.service,
        severity=ticket.severity,
        product=ticket.product,
        guarded=guarded,
    )
