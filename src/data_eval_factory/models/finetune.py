"""Local linear model. This is not a LoRA or hosted fine-tune."""

from __future__ import annotations

import math

from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.data.cleaner import tokenize


class LinearFineTune:
    def __init__(self, epochs: int = 8, learning_rate: float = 0.35, l2: float = 1e-4) -> None:
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.l2 = l2
        self._weights: dict[str, dict[str, float]] = {label: {} for label in LABELS}
        self._bias: dict[str, float] = dict.fromkeys(LABELS, 0.0)

    def fit(self, rows: list[tuple[str, str, tuple[str, ...]]], labels: list[str]) -> None:
        prepared = [
            (self._features(text, service, codes), label)
            for (text, service, codes), label in zip(rows, labels, strict=True)
        ]
        for _epoch in range(self.epochs):
            for features, label in prepared:
                scores = self._scores(features)
                probabilities = _softmax(scores)
                for class_name in LABELS:
                    error = probabilities[class_name] - (1.0 if class_name == label else 0.0)
                    penalty = error + self.l2 * self._bias[class_name]
                    self._bias[class_name] -= self.learning_rate * penalty
                    table = self._weights[class_name]
                    for token in features:
                        current = table.get(token, 0.0)
                        table[token] = current - self.learning_rate * (error + self.l2 * current)

    def predict(self, text: str, service: str, error_codes: list[str]) -> tuple[str | None, float]:
        features = self._features(text, service, tuple(error_codes))
        scores = self._scores(features)
        probabilities = _softmax(scores)
        best = max(LABELS, key=lambda label: probabilities[label])
        return best, probabilities[best]

    def _features(self, text: str, service: str, error_codes: tuple[str, ...]) -> tuple[str, ...]:
        tokens = set(tokenize(text))
        tokens.add(f"svc{service}")
        for code in error_codes:
            tokens.add(f"code{code.lower().replace('-', '')}")
        return tuple(sorted(tokens))

    def _scores(self, features: tuple[str, ...]) -> dict[str, float]:
        scores: dict[str, float] = {}
        for label in LABELS:
            table = self._weights[label]
            scores[label] = self._bias[label] + sum(table.get(token, 0.0) for token in features)
        return scores


def _softmax(scores: dict[str, float]) -> dict[str, float]:
    peak = max(scores.values()) if scores else 0.0
    weights = {label: math.exp(scores[label] - peak) for label in LABELS}
    normalizer = sum(weights.values()) or 1.0
    return {label: weight / normalizer for label, weight in weights.items()}
