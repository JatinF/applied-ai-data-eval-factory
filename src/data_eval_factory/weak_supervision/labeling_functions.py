from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from data_eval_factory.data.cleaner import tokenize
from data_eval_factory.schemas.ticket import TicketSignals

ABSTAIN = -1


@dataclass(frozen=True)
class AppliedLabel:
    name: str
    label: str | None


@dataclass(frozen=True)
class LFContext:
    history: tuple[TicketSignals, ...]


LabelFn = Callable[[TicketSignals, LFContext], str | None]


@dataclass(frozen=True)
class LabelingFunction:
    name: str
    fn: LabelFn


def _contains(text: str, *needles: str) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


def lf_password_reset(signals: TicketSignals, _: LFContext) -> str | None:
    if _contains(signals.text, "password", "credential", "mfa", "lockout"):
        return "ACCOUNT_ACCESS"
    return None


def lf_error_401_403(signals: TicketSignals, _: LFContext) -> str | None:
    codes = set(signals.error_codes)
    if codes & {"401", "403"} or _contains(
        signals.text, "401", "403", "missing scope", "forbidden"
    ):
        return "AUTHORIZATION"
    return None


def lf_database_timeout(signals: TicketSignals, _: LFContext) -> str | None:
    if "DB-57014" in signals.error_codes or _contains(signals.text, "connection pool", "db-57014"):
        return "DATABASE"
    return None


def lf_payments_service(signals: TicketSignals, _: LFContext) -> str | None:
    if signals.service == "payments":
        return "PAYMENTS"
    return None


def lf_priority_incident(signals: TicketSignals, _: LFContext) -> str | None:
    if signals.severity in {"P0", "P1"} and _contains(
        signals.text, "bridge", "repeated", "on-call"
    ):
        return "INCIDENT"
    return None


def lf_runbook_match(signals: TicketSignals, _: LFContext) -> str | None:
    checks = (
        ("password rotation", "ACCOUNT_ACCESS"),
        ("missing scope", "AUTHORIZATION"),
        ("connection pool", "DATABASE"),
        ("edge-proxy", "NETWORK"),
        ("edge proxy", "NETWORK"),
        ("chargeback", "PAYMENTS"),
        ("settlement", "PAYMENTS"),
        ("page the on-call", "INCIDENT"),
        ("open the bridge", "INCIDENT"),
    )
    for needle, label in checks:
        if needle in signals.text.lower():
            return label
    return None


def lf_similar_case(signals: TicketSignals, context: LFContext) -> str | None:
    tokens = set(tokenize(signals.text))
    best_name = ""
    best_score = 0.0
    best_label = ""
    for other in context.history:
        if other.id == signals.id or not other.recorded_type:
            continue
        other_tokens = set(tokenize(other.text))
        union = tokens | other_tokens
        score = len(tokens & other_tokens) / len(union) if union else 0.0
        if score > best_score or (score == best_score and best_name and other.id < best_name):
            best_score = score
            best_name = other.id
            best_label = other.recorded_type
    if best_score >= 0.45 and best_label:
        return best_label
    return None


def lf_domain_dictionary(signals: TicketSignals, _: LFContext) -> str | None:
    mapping = {
        "warehouse-db": "DATABASE",
        "edge-proxy": "NETWORK",
        "ledger-api": "PAYMENTS",
        "support-console": "INCIDENT",
    }
    return mapping.get(signals.product)


def lf_repeated_failures(signals: TicketSignals, _: LFContext) -> str | None:
    if _contains(signals.text, "repeated"):
        return "INCIDENT"
    return None


def lf_network_terms(signals: TicketSignals, _: LFContext) -> str | None:
    if _contains(signals.text, "packet loss", "dns", "tls", "handshake"):
        return "NETWORK"
    return None


def lf_timeout_to_network(signals: TicketSignals, _: LFContext) -> str | None:
    """Noisy rule. Database timeouts contain the same word."""
    if _contains(signals.text, "timeout"):
        return "NETWORK"
    return None


def lf_billing_keywords(signals: TicketSignals, _: LFContext) -> str | None:
    if _contains(signals.text, "invoice", "chargeback", "settlement"):
        return "PAYMENTS"
    return None


def lf_insufficient_evidence(signals: TicketSignals, _: LFContext) -> str | None:
    if signals.product == "unknown" or len(tokenize(signals.text)) < 8:
        return None
    return None


def lf_db_error_code(signals: TicketSignals, _: LFContext) -> str | None:
    if "DB-57014" in signals.error_codes:
        return "DATABASE"
    return None


def lf_pay_error_code(signals: TicketSignals, _: LFContext) -> str | None:
    if "PAY-1102" in signals.error_codes:
        return "PAYMENTS"
    return None


def lf_auth_on_payments(signals: TicketSignals, _: LFContext) -> str | None:
    if signals.service == "payments" and set(signals.error_codes) & {"401", "403"}:
        return "AUTHORIZATION"
    return None


def _registry() -> list[LabelingFunction]:
    functions: list[tuple[str, LabelFn]] = [
        ("lf_password_reset", lf_password_reset),
        ("lf_error_401_403", lf_error_401_403),
        ("lf_database_timeout", lf_database_timeout),
        ("lf_payments_service", lf_payments_service),
        ("lf_priority_incident", lf_priority_incident),
        ("lf_runbook_match", lf_runbook_match),
        ("lf_similar_case", lf_similar_case),
        ("lf_domain_dictionary", lf_domain_dictionary),
        ("lf_repeated_failures", lf_repeated_failures),
        ("lf_network_terms", lf_network_terms),
        ("lf_timeout_to_network", lf_timeout_to_network),
        ("lf_billing_keywords", lf_billing_keywords),
        ("lf_insufficient_evidence", lf_insufficient_evidence),
        ("lf_db_error_code", lf_db_error_code),
        ("lf_pay_error_code", lf_pay_error_code),
        ("lf_auth_on_payments", lf_auth_on_payments),
    ]
    return [LabelingFunction(name, fn) for name, fn in functions]


V1_LFS = _registry()[:13]
V2_LFS = _registry()


def apply_functions(
    signals: list[TicketSignals],
    functions: list[LabelingFunction],
    history: list[TicketSignals],
) -> list[list[str | None]]:
    context = LFContext(history=tuple(history))
    matrix: list[list[str | None]] = []
    for row in signals:
        matrix.append([item.fn(row, context) for item in functions])
    return matrix
