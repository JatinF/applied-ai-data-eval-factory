"""Task taxonomy for the enterprise support benchmark."""

from __future__ import annotations

LABELS: tuple[str, ...] = (
    "ACCOUNT_ACCESS",
    "AUTHORIZATION",
    "DATABASE",
    "NETWORK",
    "PAYMENTS",
    "INCIDENT",
)

TAXONOMY: dict[str, tuple[str, ...]] = {
    "classification": ("easy", "ambiguous", "multi-symptom"),
    "retrieval": ("exact evidence", "distributed evidence", "distracting evidence"),
    "reasoning": ("root cause", "prioritization", "incomplete information"),
    "agent": (
        "correct tool",
        "correct arguments",
        "abstention",
        "unsafe action prevention",
    ),
    "robustness": ("adversarial", "long context", "contradictory evidence"),
}

DISPLAY_SLICES: tuple[str, ...] = (
    "database-incidents",
    "authentication",
    "payments",
    "ambiguous-tickets",
    "missing-context",
    "cross-domain",
)
