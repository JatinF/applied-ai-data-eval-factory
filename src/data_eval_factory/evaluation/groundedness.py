from __future__ import annotations


def groundedness(answer: str | None, cited_text: str) -> float | None:
    if answer is None:
        return None
    parts = [part.strip() for part in answer.split(".") if part.strip()]
    if not parts:
        return None
    hits = sum(1 for part in parts if part in cited_text)
    return hits / len(parts)


def mean_defined(values: list[float | None]) -> float | None:
    present = [value for value in values if value is not None]
    if not present:
        return None
    return sum(present) / len(present)
