from __future__ import annotations

import hashlib
import math

DIM = 256


def embed(tokens: list[str], dim: int = DIM) -> list[float]:
    vector = [0.0] * dim
    for token in tokens:
        bucket = int(hashlib.sha256(token.encode("utf-8")).hexdigest()[:8], 16) % dim
        vector[bucket] += 1.0
    norm = math.sqrt(sum(value * value for value in vector)) or 1.0
    return [value / norm for value in vector]


def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right, strict=True))
