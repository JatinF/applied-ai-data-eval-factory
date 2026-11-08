from __future__ import annotations

from data_eval_factory.schemas.ticket import TicketSignals

KEYWORD_ORDER = (
    "lf_password_reset",
    "lf_error_401_403",
    "lf_database_timeout",
    "lf_network_terms",
    "lf_billing_keywords",
    "lf_repeated_failures",
    "lf_timeout_to_network",
)

SERVICE_LABELS = {
    "payments": "PAYMENTS",
    "database": "DATABASE",
    "network": "NETWORK",
    "platform": "INCIDENT",
    "identity": "ACCOUNT_ACCESS",
}


def reviewer_a(names: list[str], row: list[str | None]) -> str | None:
    found = dict(zip(names, row, strict=True))
    for name in KEYWORD_ORDER:
        label = found.get(name)
        if label:
            return label
    return None


def reviewer_b(signals: TicketSignals, names: list[str], row: list[str | None]) -> str | None:
    service_label = SERVICE_LABELS.get(signals.service)
    if service_label:
        return service_label
    found = dict(zip(names, row, strict=True))
    for name in ("lf_domain_dictionary", "lf_priority_incident"):
        label = found.get(name)
        if label:
            return label
    return None
