from __future__ import annotations

from data_eval_factory.benchmark.contamination import jaccard
from data_eval_factory.data.cleaner import normalize_text, tokenize


def review(source_text: str, new_text: str, strategy: str) -> tuple[str, float]:
    left = normalize_text(source_text)
    right = normalize_text(new_text)
    novelty = 1.0 - jaccard(set(tokenize(left)), set(tokenize(right)))
    if right == left or len(tokenize(right)) < 3:
        return "rejected", novelty
    if strategy in {"adversarial", "missing_context", "contradictory_context", "long_context"}:
        return "needs_review", novelty
    return "approved", novelty
