from __future__ import annotations

from data_eval_factory.benchmark.taxonomy import DISPLAY_SLICES


def display_slices(gold_type: str, tags: list[str]) -> list[str]:
    found: list[str] = []
    if gold_type == "DATABASE":
        found.append("database-incidents")
    if gold_type in {"ACCOUNT_ACCESS", "AUTHORIZATION"}:
        found.append("authentication")
    if gold_type == "PAYMENTS":
        found.append("payments")
    if "ambiguous" in tags:
        found.append("ambiguous-tickets")
    if "missing-context" in tags:
        found.append("missing-context")
    if "cross-domain" in tags:
        found.append("cross-domain")
    return [name for name in DISPLAY_SLICES if name in found]
