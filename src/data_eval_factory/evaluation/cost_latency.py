from __future__ import annotations

from data_eval_factory.evaluation.metrics import percentile


def latency_summary(samples_ms: list[float]) -> tuple[float, float]:
    return percentile(samples_ms, 50), percentile(samples_ms, 95)


def cost_note() -> dict[str, object]:
    return {"tokens": 0, "estimated_cost": None, "note": "no price applied"}
