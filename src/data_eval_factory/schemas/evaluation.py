from __future__ import annotations

from pydantic import BaseModel, Field

from data_eval_factory.schemas.benchmark import BenchmarkManifest
from data_eval_factory.schemas.label import Adjudication, LabelingReport


class SystemScore(BaseModel):
    name: str
    iteration: str
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    groundedness: float | None = None
    citation_correctness: float | None = None
    recall_at_5: float | None = None
    mrr: float | None = None
    ndcg_at_5: float | None = None
    tool_selection: float | None = None
    argument_correctness: float | None = None
    task_completion: float | None = None
    unsafe_action_rate: float | None = None
    abstention_rate: float | None = None
    appropriate_abstention: float | None = None
    p50_ms: float
    p95_ms: float
    tokens: int = 0
    estimated_cost: float | None = None


class SliceScore(BaseModel):
    slice: str
    support: int
    accuracy: float


class FailureShare(BaseModel):
    failure: str
    count: int
    share: float


class IterationReport(BaseModel):
    iteration: str
    labeling: LabelingReport
    scores: list[SystemScore]
    slices: list[SliceScore]
    failures: list[FailureShare]
    failed_tickets: int


class FactoryReport(BaseModel):
    dataset_sha256: str
    ticket_count: int
    document_count: int
    train_count: int
    validation_count: int
    test_count: int
    class_counts: dict[str, int]
    agreement_rate: float
    cohen_kappa: float
    adjudicated_count: int
    disagreements_by_label: dict[str, int]
    adjudication_examples: list[Adjudication]
    synthetic_generated: int
    synthetic_accepted: int
    synthetic_rejected: int
    synthetic_by_strategy: dict[str, int]
    duplicate_rate: float
    mean_novelty: float
    id_overlap: int
    max_train_test_jaccard: float
    hosted_llm: str
    lora: str
    label_model_backend: str
    v1: IterationReport
    v2: IterationReport
    manifests: list[BenchmarkManifest] = Field(default_factory=list)
    curation_notes: list[str]
