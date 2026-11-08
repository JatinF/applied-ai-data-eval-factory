from __future__ import annotations

from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.schemas.ticket import Ticket, TicketSignals
from data_eval_factory.weak_supervision.labeling_functions import (
    ABSTAIN,
    LabelingFunction,
    apply_functions,
)


def label_matrix(
    tickets: list[Ticket],
    functions: list[LabelingFunction],
) -> tuple[list[str], list[list[int]]]:
    history = [TicketSignals.from_ticket(ticket) for ticket in tickets if ticket.split == "train"]
    signals = [TicketSignals.from_ticket(ticket) for ticket in tickets]
    raw = apply_functions(signals, functions, history)
    index = {label: position for position, label in enumerate(LABELS)}
    encoded: list[list[int]] = []
    for row in raw:
        encoded.append([ABSTAIN if label is None else index[label] for label in row])
    names = [item.name for item in functions]
    return names, encoded
