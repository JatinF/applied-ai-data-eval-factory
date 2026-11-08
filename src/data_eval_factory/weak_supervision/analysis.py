from __future__ import annotations

from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.schemas.label import LabelingReport, LFStat
from data_eval_factory.schemas.ticket import Ticket
from data_eval_factory.weak_supervision.label_model import BACKEND, estimate_accuracies
from data_eval_factory.weak_supervision.labeling_functions import ABSTAIN


def analyze_labels(
    tickets: list[Ticket],
    names: list[str],
    matrix: list[list[int]],
) -> LabelingReport:
    total = len(matrix) or 1
    covered = 0
    overlapped = 0
    conflicted = 0
    accuracies = estimate_accuracies(matrix)
    stats: list[LFStat] = []
    for column, name in enumerate(names):
        votes = 0
        gold_correct = 0
        gold_total = 0
        shared = 0
        conflicts = 0
        for row_index, row in enumerate(matrix):
            value = row[column]
            if value == ABSTAIN:
                continue
            votes += 1
            others = [
                other
                for index, other in enumerate(row)
                if index != column and other != ABSTAIN
            ]
            if others:
                shared += 1
                if any(other != value for other in others):
                    conflicts += 1
            gold_total += 1
            if LABELS[value] == tickets[row_index].gold_type:
                gold_correct += 1
        stats.append(
            LFStat(
                name=name,
                coverage=votes / total,
                abstention_rate=1 - (votes / total),
                overlap_with_others=shared / total,
                conflicts_with_others=conflicts / total,
                estimated_accuracy=accuracies[column],
                gold_accuracy=(gold_correct / gold_total) if gold_total else None,
                votes=votes,
            )
        )
    for row in matrix:
        present = [value for value in row if value != ABSTAIN]
        if present:
            covered += 1
        if len(present) >= 2:
            overlapped += 1
        if len(set(present)) >= 2:
            conflicted += 1
    return LabelingReport(
        lf_names=names,
        coverage=covered / total,
        overlap=overlapped / total,
        conflict=conflicted / total,
        labeling_functions=stats,
        backend=BACKEND,
        used_gold_to_fit=False,
    )
