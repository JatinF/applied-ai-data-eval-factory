from __future__ import annotations

from pydantic import BaseModel, Field


class BenchmarkItem(BaseModel):
    id: str
    version: str
    ticket_id: str
    tasks: list[str]
    difficulty: str
    slices: list[str]
    rubric_id: str
    gold_type: str
    gold_tool: str
    relevant_doc_ids: list[str]


class BenchmarkManifest(BaseModel):
    version: str
    item_count: int
    task_counts: dict[str, int]
    difficulty_counts: dict[str, int]
    slice_counts: dict[str, int]
    dataset_sha256: str
    notes: list[str] = Field(default_factory=list)
