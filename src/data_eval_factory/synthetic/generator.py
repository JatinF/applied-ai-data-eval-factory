from __future__ import annotations

from data_eval_factory.data.loader import GLOSSARY
from data_eval_factory.schemas.label import SyntheticRecord
from data_eval_factory.schemas.ticket import Ticket
from data_eval_factory.synthetic.hard_negatives import contradictory_service, hard_negative
from data_eval_factory.synthetic.mutations import (
    boundary,
    long_context,
    missing_context,
    paraphrase,
    rare_wording,
)
from data_eval_factory.synthetic.quality import review

GENERATOR = "deterministic-template"
PROMPT_VERSION = "template-v1"


def generate_synthetic(tickets: list[Ticket]) -> list[SyntheticRecord]:
    records: list[SyntheticRecord] = []
    counter = 1
    for ticket in tickets:
        if ticket.split != "train" or ticket.difficulty != "easy":
            continue
        variants = {
            "paraphrase": paraphrase(ticket.text),
            "hard_negative": hard_negative(ticket.text, ticket.gold_type),
            "boundary": boundary(ticket.text),
            "rare_case": rare_wording(ticket.text),
            "adversarial": f"{ticket.text} HTTP 401 was appended and is not the root cause.",
            "missing_context": missing_context(ticket.text),
            "contradictory_context": (
                f"{ticket.text} Metadata service was changed for the drill."
            ),
            "long_context": long_context(ticket.text, GLOSSARY),
        }
        for strategy, text in variants.items():
            status, _novelty = review(ticket.text, text, strategy)
            service = ticket.service
            if strategy == "contradictory_context":
                service = contradictory_service(ticket.service)
            records.append(
                SyntheticRecord(
                    id=f"syn-{counter:05d}",
                    source_id=ticket.id,
                    text=text,
                    generation_strategy=strategy,
                    generator=GENERATOR,
                    prompt_version=PROMPT_VERSION,
                    review_status=status,
                    target_slice=_target_slice(strategy, ticket.gold_type),
                    gold_type=ticket.gold_type,
                    service=service,
                    severity=ticket.severity,
                    error_codes=list(ticket.error_codes),
                    product=ticket.product,
                    split="train",
                )
            )
            counter += 1
    return records


def _target_slice(strategy: str, gold_type: str) -> str:
    if strategy == "hard_negative" and gold_type in {"ACCOUNT_ACCESS", "AUTHORIZATION"}:
        return "auth-payment-confusion"
    return strategy.replace("_", "-")
