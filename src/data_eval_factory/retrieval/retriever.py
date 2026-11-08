from __future__ import annotations

from dataclasses import dataclass

from data_eval_factory.data.cleaner import tokenize
from data_eval_factory.retrieval.embeddings import embed
from data_eval_factory.retrieval.index import SearchIndex
from data_eval_factory.retrieval.reranker import combine
from data_eval_factory.schemas.ticket import Document


@dataclass(frozen=True)
class Hit:
    document: Document
    score: float


def search(index: SearchIndex, query: str, k: int = 5) -> list[Hit]:
    tokens = tokenize(query)
    vector = embed(tokens)
    ranked: list[Hit] = []
    for item in index.documents:
        score = combine(index.bm25(tokens, item), vector, item.vector)
        ranked.append(Hit(document=item.document, score=score))
    ranked.sort(key=lambda hit: (-hit.score, hit.document.id))
    return ranked[:k]
