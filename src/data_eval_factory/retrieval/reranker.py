from __future__ import annotations

from data_eval_factory.retrieval.embeddings import cosine


def combine(bm25_score: float, query_vector: list[float], doc_vector: tuple[float, ...]) -> float:
    lexical = bm25_score / (1.0 + bm25_score)
    return (0.8 * lexical) + (0.2 * cosine(query_vector, list(doc_vector)))
