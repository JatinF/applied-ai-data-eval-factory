from __future__ import annotations

from collections import Counter

from data_eval_factory.data.cleaner import tokenize
from data_eval_factory.schemas.ticket import Ticket


def profile_tickets(tickets: list[Ticket]) -> dict[str, object]:
    lengths = [len(tokenize(ticket.text)) for ticket in tickets]
    missing = sum(1 for ticket in tickets if not ticket.text or not ticket.product)
    counts = Counter(ticket.gold_type for ticket in tickets)
    ordered = sorted(lengths)
    midpoint = ordered[len(ordered) // 2] if ordered else 0
    return {
        "count": len(tickets),
        "missing_required": missing,
        "class_counts": dict(sorted(counts.items())),
        "token_p50": midpoint,
        "token_min": min(lengths) if lengths else 0,
        "token_max": max(lengths) if lengths else 0,
    }
