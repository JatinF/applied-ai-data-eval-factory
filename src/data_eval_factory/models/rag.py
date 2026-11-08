from __future__ import annotations

from data_eval_factory.benchmark.taxonomy import LABELS
from data_eval_factory.retrieval.retriever import Hit


def classify_retrieved(hits: list[Hit]) -> str | None:
    if not hits or hits[0].score <= 0:
        return None
    totals = dict.fromkeys(LABELS, 0.0)
    for hit in hits[:3]:
        totals[hit.document.category] += hit.score
    best = max(LABELS, key=lambda label: totals[label])
    if totals[best] <= 0:
        return None
    return best


def answer_retrieved(hits: list[Hit]) -> tuple[str | None, list[str]]:
    if not hits or hits[0].score <= 0:
        return None, []
    citation = hits[0].document.text.split(".", maxsplit=1)[0].strip()
    return citation, [hits[0].document.id]
