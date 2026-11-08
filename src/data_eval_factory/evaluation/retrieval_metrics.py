from __future__ import annotations

import math


def recall_at_k(ranked_ids: list[str], relevant: list[str], k: int) -> float:
    if not relevant:
        return 0.0
    found = set(ranked_ids[:k]) & set(relevant)
    return len(found) / len(relevant)


def reciprocal_rank(ranked_ids: list[str], relevant: list[str]) -> float:
    relevant_ids = set(relevant)
    for index, doc_id in enumerate(ranked_ids, start=1):
        if doc_id in relevant_ids:
            return 1 / index
    return 0.0


def ndcg_at_k(ranked_ids: list[str], relevant: list[str], k: int) -> float:
    relevant_ids = set(relevant)
    gains = [1.0 if doc_id in relevant_ids else 0.0 for doc_id in ranked_ids[:k]]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal = min(k, len(relevant_ids))
    idcg = sum(1 / math.log2(index + 2) for index in range(ideal))
    if idcg == 0:
        return 0.0
    return dcg / idcg
