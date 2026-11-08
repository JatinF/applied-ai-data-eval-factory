from __future__ import annotations

from pydantic import BaseModel, Field


class Ticket(BaseModel):
    """Synthetic support ticket. gold_type is the generator root cause."""

    id: str
    text: str
    service: str
    severity: str
    error_codes: list[str] = Field(default_factory=list)
    product: str
    recorded_type: str
    historical_resolution: str
    relevant_doc_ids: list[str]
    gold_type: str
    gold_tool: str
    split: str
    difficulty: str
    slices: list[str]
    tasks: list[str]


class TicketSignals(BaseModel):
    """Fields a labeling function may read. Gold is not included."""

    id: str
    text: str
    service: str
    severity: str
    error_codes: list[str]
    product: str
    recorded_type: str
    historical_resolution: str
    relevant_doc_ids: list[str]

    @classmethod
    def from_ticket(cls, ticket: Ticket) -> TicketSignals:
        return cls.model_validate(
            ticket.model_dump(
                include={
                    "id",
                    "text",
                    "service",
                    "severity",
                    "error_codes",
                    "product",
                    "recorded_type",
                    "historical_resolution",
                    "relevant_doc_ids",
                }
            )
        )


class Document(BaseModel):
    id: str
    title: str
    category: str
    kind: str
    text: str
