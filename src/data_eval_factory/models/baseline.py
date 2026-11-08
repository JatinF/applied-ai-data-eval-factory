from __future__ import annotations

import math

from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.data.cleaner import tokenize


class BaselineClassifier:
    """Multinomial naive Bayes trained on weak labels and ticket text."""

    def __init__(self) -> None:
        self._token_given: dict[str, dict[str, float]] = {}
        self._prior: dict[str, float] = {}
        self._vocab: set[str] = set()

    def fit(self, texts: list[str], labels: list[str]) -> None:
        counts: dict[str, dict[str, int]] = {label: {} for label in LABELS}
        label_tokens = dict.fromkeys(LABELS, 0)
        label_rows = dict.fromkeys(LABELS, 0)
        for text, label in zip(texts, labels, strict=True):
            if label not in counts:
                continue
            label_rows[label] += 1
            seen: set[str] = set()
            for token in tokenize(text):
                if token in seen:
                    continue
                seen.add(token)
                counts[label][token] = counts[label].get(token, 0) + 1
                label_tokens[label] += 1
                self._vocab.add(token)
        total_rows = sum(label_rows.values()) or 1
        vocab_size = len(self._vocab) or 1
        for label in LABELS:
            self._prior[label] = (label_rows[label] + 1) / (total_rows + len(LABELS))
            denom = label_tokens[label] + vocab_size
            self._token_given[label] = {
                token: (counts[label].get(token, 0) + 1) / denom for token in sorted(self._vocab)
            }

    def predict(self, text: str) -> tuple[str | None, float]:
        if not self._vocab:
            return None, 0.0
        tokens = set(tokenize(text))
        scores: dict[str, float] = {}
        for label in LABELS:
            score = math.log(self._prior[label])
            table = self._token_given[label]
            for token in tokens:
                if token in table:
                    score += math.log(table[token])
            scores[label] = score
        peak = max(scores.values())
        weights = {label: math.exp(scores[label] - peak) for label in LABELS}
        normalizer = sum(weights.values())
        best = max(LABELS, key=lambda label: weights[label])
        return best, weights[best] / normalizer
