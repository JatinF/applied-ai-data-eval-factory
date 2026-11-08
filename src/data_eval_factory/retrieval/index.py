from __future__ import annotations

import math
from dataclasses import dataclass

from data_eval_factory.data.cleaner import tokenize
from data_eval_factory.retrieval.embeddings import embed
from data_eval_factory.schemas.ticket import Document


@dataclass(frozen=True)
class IndexedDocument:
    document: Document
    tokens: tuple[str, ...]
    vector: tuple[float, ...]
    length: int


@dataclass(frozen=True)
class SearchIndex:
    documents: tuple[IndexedDocument, ...]
    doc_freq: dict[str, int]
    avg_length: float

    @classmethod
    def build(cls, documents: list[Document]) -> SearchIndex:
        indexed: list[IndexedDocument] = []
        frequencies: dict[str, int] = {}
        for document in documents:
            tokens = tokenize(document.title + " " + document.text)
            for token in set(tokens):
                frequencies[token] = frequencies.get(token, 0) + 1
            vector = embed(tokens)
            indexed.append(
                IndexedDocument(
                    document=document,
                    tokens=tuple(tokens),
                    vector=tuple(vector),
                    length=len(tokens),
                )
            )
        average = sum(item.length for item in indexed) / len(indexed) if indexed else 1.0
        return cls(documents=tuple(indexed), doc_freq=frequencies, avg_length=average)

    def bm25(
        self,
        query_tokens: list[str],
        item: IndexedDocument,
        k1: float = 1.5,
        b: float = 0.75,
    ) -> float:
        counts: dict[str, int] = {}
        for token in item.tokens:
            counts[token] = counts.get(token, 0) + 1
        score = 0.0
        total_docs = len(self.documents) or 1
        for token in query_tokens:
            if token not in counts:
                continue
            df = self.doc_freq.get(token, 0)
            idf = math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            freq = counts[token]
            denom = freq + k1 * (1 - b + b * item.length / (self.avg_length or 1.0))
            score += idf * (freq * (k1 + 1)) / (denom or 1.0)
        return score
