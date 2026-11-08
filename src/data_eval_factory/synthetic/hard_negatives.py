from __future__ import annotations


def hard_negative(text: str, gold_type: str) -> str:
    bait = {
        "ACCOUNT_ACCESS": "Invoice settlement was mentioned by mistake.",
        "AUTHORIZATION": "Connection pool wording was pasted beside the denial.",
        "DATABASE": "Chargeback wording was pasted beside the pool alert.",
        "NETWORK": "Password rotation wording was pasted beside the proxy alert.",
        "PAYMENTS": "DNS packet-loss wording was pasted beside the ledger alert.",
        "INCIDENT": "A single invoice number was pasted beside the bridge note.",
    }
    return f"{text} {bait[gold_type]}"


def contradictory_service(service: str) -> str:
    order = ["identity", "payments", "database", "network", "platform", "unknown"]
    if service not in order:
        return "unknown"
    return order[(order.index(service) + 1) % len(order)]
