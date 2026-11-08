from __future__ import annotations

from data_eval_factory.benchmark.taxonomy import DISPLAY_SLICES
from data_eval_factory.schemas.evaluation import SliceScore
from data_eval_factory.schemas.ticket import Ticket


def slice_accuracy(tickets: list[Ticket], predicted: list[str | None]) -> list[SliceScore]:
    scores: list[SliceScore] = []
    for name in DISPLAY_SLICES:
        chosen = [
            guess == ticket.gold_type
            for ticket, guess in zip(tickets, predicted, strict=True)
            if name in ticket.slices
        ]
        accuracy = sum(1 for item in chosen if item) / len(chosen) if chosen else 0.0
        scores.append(SliceScore(slice=name, support=len(chosen), accuracy=accuracy))
    return scores
