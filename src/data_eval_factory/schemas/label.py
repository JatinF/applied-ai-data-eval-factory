from __future__ import annotations

from pydantic import BaseModel, Field


class Adjudication(BaseModel):
    sample_id: str
    reviewer_a: str | None
    reviewer_b: str | None
    agreement: bool
    adjudicated_label: str
    reason: str


class LFStat(BaseModel):
    name: str
    coverage: float
    abstention_rate: float
    overlap_with_others: float
    conflicts_with_others: float
    estimated_accuracy: float
    gold_accuracy: float | None
    votes: int


class LabelingReport(BaseModel):
    lf_names: list[str]
    coverage: float
    overlap: float
    conflict: float
    labeling_functions: list[LFStat]
    backend: str
    used_gold_to_fit: bool = False


class SyntheticRecord(BaseModel):
    id: str
    source_id: str
    text: str
    generation_strategy: str
    generator: str
    prompt_version: str
    review_status: str
    target_slice: str
    gold_type: str
    service: str
    severity: str
    error_codes: list[str] = Field(default_factory=list)
    product: str
    split: str
