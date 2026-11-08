from __future__ import annotations

from data_eval_factory.schemas.evaluation import FactoryReport, SystemScore


def _find(report: FactoryReport, iteration: str, name: str) -> SystemScore:
    block = report.v2 if iteration == "v2" else report.v1
    for score in block.scores:
        if score.name == name:
            return score
    raise KeyError(name)


def regression_messages(
    current: FactoryReport,
    baseline: FactoryReport,
    *,
    max_f1_drop: float,
    max_groundedness_drop: float,
) -> list[str]:
    messages: list[str] = []
    current_model = _find(current, "v2", "linear_finetune")
    baseline_model = _find(baseline, "v2", "linear_finetune")
    if baseline_model.f1_macro - current_model.f1_macro > max_f1_drop:
        messages.append(
            "linear_finetune F1 dropped from "
            f"{baseline_model.f1_macro:.4f} to {current_model.f1_macro:.4f}"
        )
    current_prompt = _find(current, "v2", "prompt_template")
    baseline_prompt = _find(baseline, "v2", "prompt_template")
    if (
        baseline_prompt.groundedness is not None
        and current_prompt.groundedness is not None
        and baseline_prompt.groundedness - current_prompt.groundedness > max_groundedness_drop
    ):
        messages.append(
            "prompt groundedness dropped from "
            f"{baseline_prompt.groundedness:.4f} to {current_prompt.groundedness:.4f}"
        )
    current_agent = _find(current, "v2", "guarded_agent")
    baseline_agent = _find(baseline, "v2", "guarded_agent")
    if (
        current_agent.unsafe_action_rate is not None
        and baseline_agent.unsafe_action_rate is not None
        and current_agent.unsafe_action_rate > baseline_agent.unsafe_action_rate
    ):
        messages.append(
            "unsafe action rate rose from "
            f"{baseline_agent.unsafe_action_rate:.4f} to {current_agent.unsafe_action_rate:.4f}"
        )
    return messages
