from __future__ import annotations

from data_eval_factory.data.cleaner import tokenize
from data_eval_factory.schemas.ticket import Ticket


def jaccard(left: set[str], right: set[str]) -> float:
    if not left and not right:
        return 1.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def contamination(tickets: list[Ticket]) -> tuple[int, float]:
    train = [ticket for ticket in tickets if ticket.split == "train"]
    test = [ticket for ticket in tickets if ticket.split == "test"]
    overlap = len({ticket.id for ticket in train} & {ticket.id for ticket in test})
    train_sets = [set(tokenize(ticket.text)) for ticket in train]
    max_score = 0.0
    for ticket in test:
        tokens = set(tokenize(ticket.text))
        if not train_sets:
            continue
        max_score = max(max_score, max(jaccard(tokens, other) for other in train_sets))
    return overlap, max_score
