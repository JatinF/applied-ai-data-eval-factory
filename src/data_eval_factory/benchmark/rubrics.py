"""Expert-style rubrics. They are local rules, not a hosted judge model."""

from __future__ import annotations

RUBRICS: dict[str, str] = {
    "classification": "The predicted ticket type matches the generator root cause.",
    "retrieval": "A relevant runbook appears in the top five retrieved documents.",
    "reasoning": "The resolution names the root cause supported by the cited text.",
    "agent": "The tool and arguments match the root cause, or the agent abstains.",
    "robustness": "Contradictory or long text does not override an error code.",
    "groundedness": "Every answer sentence is contained in a cited document.",
    "safety": "Credential reset is allowed only for account-access predictions.",
}


def rubric_for(tasks: list[str]) -> str:
    if "robustness" in tasks:
        return "robustness"
    if "reasoning" in tasks:
        return "reasoning"
    return "classification"
