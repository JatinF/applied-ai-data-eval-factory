from __future__ import annotations

from data_eval_factory.retrieval.retriever import Hit

UNSUPPORTED = "Restart every production service to be safe"


def _head(text: str) -> str:
    marker = "Glossary appendix"
    if marker in text:
        return text.split(marker, maxsplit=1)[0]
    return text


def classify_prompt(text: str, *, strip_appendix: bool) -> str | None:
    lowered = _head(text).lower() if strip_appendix else text.lower()
    if any(token in lowered for token in ("401", "403", "missing scope", "forbidden")):
        return "AUTHORIZATION"
    if any(token in lowered for token in ("password", "credential", "mfa", "lockout")):
        return "ACCOUNT_ACCESS"
    if any(token in lowered for token in ("invoice", "chargeback", "settlement")):
        return "PAYMENTS"
    if any(token in lowered for token in ("connection pool", "db-57014")):
        return "DATABASE"
    if any(token in lowered for token in ("dns", "packet loss", "tls", "handshake")):
        return "NETWORK"
    if any(token in lowered for token in ("bridge", "repeated", "on-call")):
        return "INCIDENT"
    return None


def answer_prompt(hits: list[Hit], *, strip_unsupported: bool) -> tuple[str | None, list[str]]:
    if not hits or hits[0].score <= 0:
        return None, []
    citation = hits[0].document.text.split(".", maxsplit=1)[0].strip()
    if strip_unsupported:
        return citation, [hits[0].document.id]
    return f"{citation}. {UNSUPPORTED}.", [hits[0].document.id]
