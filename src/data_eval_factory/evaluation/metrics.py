from __future__ import annotations

import math

from data_eval_factory.benchmark.taxonomy import LABELS


def accuracy(truth: list[str], predicted: list[str | None]) -> float:
    if not truth:
        return 0.0
    hits = sum(1 for gold, guess in zip(truth, predicted, strict=True) if gold == guess)
    return hits / len(truth)


def _prf(truth: list[str], predicted: list[str | None], label: str) -> tuple[float, float, float]:
    pairs = list(zip(truth, predicted, strict=True))
    tp = sum(1 for gold, guess in pairs if gold == label and guess == label)
    fp = sum(1 for gold, guess in pairs if gold != label and guess == label)
    fn = sum(1 for gold, guess in pairs if gold == label and guess != label)
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return precision, recall, f1


def macro_scores(truth: list[str], predicted: list[str | None]) -> tuple[float, float, float]:
    rows = [_prf(truth, predicted, label) for label in LABELS]
    count = len(rows) or 1
    return (
        sum(item[0] for item in rows) / count,
        sum(item[1] for item in rows) / count,
        sum(item[2] for item in rows) / count,
    )


def cohen_kappa(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    labels = sorted(set(left) | set(right))
    total = len(left)
    matrix = {(gold, guess): 0 for gold in labels for guess in labels}
    for gold, guess in zip(left, right, strict=True):
        matrix[(gold, guess)] += 1
    observed = sum(matrix[(label, label)] for label in labels) / total
    row_rate = [sum(matrix[(label, other)] for other in labels) / total for label in labels]
    col_rate = [sum(matrix[(other, label)] for other in labels) / total for label in labels]
    expected = sum(first * second for first, second in zip(row_rate, col_rate, strict=True))
    if expected == 1:
        return 1.0
    return (observed - expected) / (1 - expected)


def percentile(values: list[float], percent: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = math.ceil(percent / 100 * len(ordered)) - 1
    rank = min(len(ordered) - 1, max(0, rank))
    return ordered[rank]
