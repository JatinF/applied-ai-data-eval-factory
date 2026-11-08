from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Sequence
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from data_eval_factory.benchmark.slices import display_slices
from data_eval_factory.data.cleaner import normalize_text
from data_eval_factory.data.versioning import split_for
from data_eval_factory.schemas.ticket import Document, Ticket

GLOSSARY = (
    "Glossary appendix, not a symptom list. Operators sometimes mention invoices, "
    "packet loss, password rotation, connection pools, and bridge calls while "
    "documenting unrelated history. The words timeout and invoice in this appendix "
    "are definitions. They do not describe the current ticket."
)

RESOLUTIONS = {
    "ACCOUNT_ACCESS": "Reset the credential, confirm MFA, and unlock the account.",
    "AUTHORIZATION": "Grant the missing scope and retry the request.",
    "DATABASE": "Raise the connection pool and retry the timed-out statement.",
    "NETWORK": "Fail over the edge proxy after the DNS or TLS fault clears.",
    "PAYMENTS": "Hold settlement, reconcile the invoice, and replay the charge.",
    "INCIDENT": "Open the bridge, page the primary on-call, and post status.",
}

TOOLS = {
    "ACCOUNT_ACCESS": "reset_credentials",
    "AUTHORIZATION": "lookup_runbook",
    "DATABASE": "restart_service",
    "NETWORK": "restart_service",
    "PAYMENTS": "lookup_runbook",
    "INCIDENT": "page_oncall",
}


def repo_root() -> Path:
    env = os.environ.get("DATA_EVAL_ROOT")
    if env:
        return Path(env).resolve()
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "pyproject.toml").exists() and (parent / "configs").exists():
            return parent
    raise FileNotFoundError("repository root not found")


def build_documents() -> list[Document]:
    specs = [
        ("runbook-account-access", "Password rotation runbook", "ACCOUNT_ACCESS", "runbook"),
        ("product-identity", "Identity gateway product note", "ACCOUNT_ACCESS", "product"),
        ("runbook-authorization", "Scope and HTTP 403 runbook", "AUTHORIZATION", "runbook"),
        ("product-authz", "Authorization product note", "AUTHORIZATION", "product"),
        ("runbook-database", "Connection pool runbook", "DATABASE", "runbook"),
        ("product-warehouse", "Warehouse database note", "DATABASE", "product"),
        ("runbook-network", "Edge proxy DNS runbook", "NETWORK", "runbook"),
        ("product-edge", "Edge proxy product note", "NETWORK", "product"),
        ("runbook-payments", "Settlement and invoice runbook", "PAYMENTS", "runbook"),
        ("product-ledger", "Ledger API product note", "PAYMENTS", "product"),
        ("runbook-incident", "Repeated failure bridge runbook", "INCIDENT", "runbook"),
        ("product-support", "Support console note", "INCIDENT", "product"),
    ]
    bodies = {
        "ACCOUNT_ACCESS": "Reset the password, clear the lockout, and confirm MFA enrollment.",
        "AUTHORIZATION": "HTTP 401 and 403 mean a missing scope. Do not reset the password.",
        "DATABASE": "Statement timeout with DB-57014 means the connection pool is exhausted.",
        "NETWORK": "DNS failure or TLS handshake loss on the edge proxy is a network fault.",
        "PAYMENTS": "Invoice, settlement, and chargeback work stays in the ledger runbook.",
        "INCIDENT": "Repeated customer-facing failures open a bridge and page the on-call.",
    }
    documents: list[Document] = []
    for doc_id, title, category, kind in specs:
        documents.append(
            Document(
                id=doc_id,
                title=title,
                category=category,
                kind=kind,
                text=f"{title}. {bodies[category]}",
            )
        )
    return documents


def _flip(label: str, sample_id: str) -> str:
    labels = list(RESOLUTIONS)
    digest = int(hashlib.sha256(sample_id.encode("utf-8")).hexdigest()[8:10], 16)
    if digest % 7 != 0:
        return label
    return labels[(labels.index(label) + 1) % len(labels)]


def _ticket(
    index: int,
    gold: str,
    text: str,
    *,
    service: str,
    severity: str,
    error_codes: list[str],
    product: str,
    difficulty: str,
    tags: list[str],
    tasks: list[str],
) -> Ticket:
    sample_id = f"ticket-{index:04d}"
    slices = display_slices(gold, tags)
    return Ticket(
        id=sample_id,
        text=normalize_text(text),
        service=service,
        severity=severity,
        error_codes=error_codes,
        product=product,
        recorded_type=_flip(gold, sample_id),
        historical_resolution=RESOLUTIONS[gold],
        relevant_doc_ids=[f"runbook-{gold.lower().replace('_', '-')}", _product_doc(gold)],
        gold_type=gold,
        gold_tool=TOOLS[gold],
        split=split_for(sample_id),
        difficulty=difficulty,
        slices=slices,
        tasks=tasks,
    )


def _product_doc(gold: str) -> str:
    return {
        "ACCOUNT_ACCESS": "product-identity",
        "AUTHORIZATION": "product-authz",
        "DATABASE": "product-warehouse",
        "NETWORK": "product-edge",
        "PAYMENTS": "product-ledger",
        "INCIDENT": "product-support",
    }[gold]


def build_tickets() -> list[Ticket]:
    tickets: list[Ticket] = []
    index = 1
    easy = {
        "ACCOUNT_ACCESS": (
            "identity",
            "identity-gateway",
            "P2",
            [],
            "Unable to authenticate after password rotation for identity-gateway.",
        ),
        "AUTHORIZATION": (
            "identity",
            "identity-gateway",
            "P2",
            ["401"],
            "HTTP 401 forbidden missing scope on identity-gateway.",
        ),
        "DATABASE": (
            "database",
            "warehouse-db",
            "P1",
            ["DB-57014"],
            "Database statement timeout because the connection pool is exhausted. DB-57014.",
        ),
        "NETWORK": (
            "network",
            "edge-proxy",
            "P2",
            [],
            "TLS handshake packet loss and DNS failure on edge-proxy.",
        ),
        "PAYMENTS": (
            "payments",
            "ledger-api",
            "P2",
            ["PAY-1102"],
            "Invoice settlement failed with chargeback PAY-1102 on ledger-api.",
        ),
        "INCIDENT": (
            "platform",
            "support-console",
            "P0",
            [],
            "Repeated customer-facing failures. Open the bridge and page on-call.",
        ),
    }
    for _copy in range(30):
        for gold, (service, product, severity, codes, text) in easy.items():
            variant = f"{text} Case {_copy}."
            tickets.append(
                _ticket(
                    index,
                    gold,
                    variant,
                    service=service,
                    severity=severity,
                    error_codes=codes,
                    product=product,
                    difficulty="easy",
                    tags=["easy"],
                    tasks=["classification", "retrieval", "reasoning", "agent"],
                )
            )
            index += 1
    vague = "The workflow failed after the last change and the user cannot continue."
    for _copy in range(6):
        for gold in RESOLUTIONS:
            tickets.append(
                _ticket(
                    index,
                    gold,
                    f"{vague} Note {_copy}.",
                    service="unknown",
                    severity="P3",
                    error_codes=[],
                    product="unknown",
                    difficulty="ambiguous",
                    tags=["missing-context"],
                    tasks=["classification", "reasoning", "agent", "retrieval"],
                )
            )
            index += 1
    contradictory = [
        (
            "DATABASE",
            "Packet loss and DNS wording were pasted by mistake, but DB-57014 is the fault.",
            "database",
            ["DB-57014"],
            "warehouse-db",
        ),
        (
            "AUTHORIZATION",
            "Invoice wording was copied into an HTTP 403 missing scope denial.",
            "payments",
            ["403"],
            "ledger-api",
        ),
        (
            "NETWORK",
            "Connection pool wording was copied, but the edge-proxy DNS failure is the fault.",
            "network",
            [],
            "edge-proxy",
        ),
    ]
    for _copy in range(8):
        for gold, text, service, codes, product in contradictory:
            tickets.append(
                _ticket(
                    index,
                    gold,
                    f"{text} Observation {_copy}.",
                    service=service,
                    severity="P1",
                    error_codes=codes,
                    product=product,
                    difficulty="ambiguous",
                    tags=["cross-domain", "contradictory"],
                    tasks=["classification", "reasoning", "robustness", "agent", "retrieval"],
                )
            )
            index += 1
    for _copy in range(6):
        tickets.append(
            _ticket(
                index,
                "AUTHORIZATION",
                "HTTP 403 missing scope while the payments service invoice is also mentioned. "
                f"Mix {_copy}.",
                service="payments",
                severity="P2",
                error_codes=["403"],
                product="ledger-api",
                difficulty="ambiguous",
                tags=["ambiguous", "cross-domain"],
                tasks=["classification", "reasoning", "retrieval", "agent"],
            )
        )
        index += 1
        tickets.append(
            _ticket(
                index,
                "DATABASE",
                "Connection pool exhausted and the edge network timeout was reported too. "
                f"Mix {_copy}.",
                service="database",
                severity="P1",
                error_codes=["DB-57014"],
                product="warehouse-db",
                difficulty="multi-symptom",
                tags=["ambiguous", "multi-symptom"],
                tasks=["classification", "reasoning", "retrieval", "agent"],
            )
        )
        index += 1
        tickets.append(
            _ticket(
                index,
                "INCIDENT",
                "Repeated failures across password and invoice symptoms. Priority is the bridge. "
                f"Mix {_copy}.",
                service="platform",
                severity="P0",
                error_codes=[],
                product="support-console",
                difficulty="multi-symptom",
                tags=["multi-symptom", "ambiguous"],
                tasks=["classification", "reasoning", "agent"],
            )
        )
        index += 1
    for _copy in range(2):
        for gold, (service, product, severity, codes, text) in easy.items():
            tickets.append(
                _ticket(
                    index,
                    gold,
                    f"{text} Long record {_copy}. {GLOSSARY}",
                    service=service,
                    severity=severity,
                    error_codes=codes,
                    product=product,
                    difficulty="ambiguous",
                    tags=["long-context"],
                    tasks=["classification", "retrieval", "robustness", "agent"],
                )
            )
            index += 1
    return tickets


def write_jsonl(path: Path, rows: Sequence[object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for row in rows:
        if hasattr(row, "model_dump"):
            payload = row.model_dump()
        else:
            payload = row
        lines.append(json.dumps(payload, sort_keys=True))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


RecordT = TypeVar("RecordT", bound=BaseModel)


def read_jsonl(path: Path, model: type[RecordT]) -> list[RecordT]:
    rows: list[RecordT] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(model.model_validate_json(line))
    return rows


def materialize_raw(root: Path) -> tuple[list[Ticket], list[Document]]:
    tickets = build_tickets()
    documents = build_documents()
    write_jsonl(root / "data" / "raw" / "tickets.jsonl", tickets)
    write_jsonl(root / "data" / "raw" / "documents.jsonl", documents)
    return tickets, documents


def load_raw(root: Path) -> tuple[list[Ticket], list[Document]]:
    ticket_path = root / "data" / "raw" / "tickets.jsonl"
    document_path = root / "data" / "raw" / "documents.jsonl"
    if not ticket_path.exists() or not document_path.exists():
        return materialize_raw(root)
    return read_jsonl(ticket_path, Ticket), read_jsonl(document_path, Document)
