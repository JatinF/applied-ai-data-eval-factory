"""Probabilistic label model in the Snorkel style.

The official snorkel package is not imported. This fit uses leave-one-out
agreement among labeling functions and does not read gold labels.
"""

from __future__ import annotations

import math
from collections import Counter

from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.weak_supervision.labeling_functions import ABSTAIN

BACKEND = "local-probabilistic-v1"


def _clamp(value: float) -> float:
    return min(0.97, max(0.51, value))


def estimate_accuracies(matrix: list[list[int]]) -> list[float]:
    if not matrix:
        return []
    width = len(matrix[0])
    accuracies: list[float] = []
    for column in range(width):
        correct = 0
        total = 0
        for row in matrix:
            if row[column] == ABSTAIN:
                continue
            others = [
                value
                for index, value in enumerate(row)
                if index != column and value != ABSTAIN
            ]
            if not others:
                continue
            counts = Counter(others)
            winner, votes = counts.most_common(1)[0]
            tied = sum(1 for count in counts.values() if count == votes) > 1
            if tied:
                continue
            total += 1
            correct += int(row[column] == winner)
        accuracies.append(_clamp(correct / total) if total else 0.7)
    return accuracies


def predict(
    matrix: list[list[int]],
    accuracies: list[float],
) -> tuple[list[str | None], list[float]]:
    classes = len(LABELS)
    predictions: list[str | None] = []
    confidence: list[float] = []
    for row in matrix:
        if all(value == ABSTAIN for value in row):
            predictions.append(None)
            confidence.append(0.0)
            continue
        scores = [0.0] * classes
        for column, value in enumerate(row):
            if value == ABSTAIN:
                continue
            accuracy = accuracies[column]
            residual = (1.0 - accuracy) / (classes - 1)
            for label_id in range(classes):
                probability = accuracy if value == label_id else residual
                scores[label_id] += math.log(probability)
        peak = max(scores)
        weights = [math.exp(score - peak) for score in scores]
        normalizer = sum(weights)
        probabilities = [weight / normalizer for weight in weights]
        best = max(range(classes), key=lambda label_id: probabilities[label_id])
        predictions.append(LABELS[best])
        confidence.append(probabilities[best])
    return predictions, confidence
