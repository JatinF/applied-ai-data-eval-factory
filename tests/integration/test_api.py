from __future__ import annotations

from fastapi.testclient import TestClient

from data_eval_factory.api.app import create_app
from data_eval_factory.evaluation.runner import Runtime


def test_api_round_trip(runtime: Runtime) -> None:
    client = TestClient(create_app(runtime))
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["hosted_llm"] == "not-run"
    classified = client.post(
        "/v1/classify",
        json={
            "text": "HTTP 403 missing scope",
            "service": "payments",
            "error_codes": ["403"],
            "product": "ledger-api",
        },
    )
    assert classified.status_code == 200
    assert classified.json()["label"] == "AUTHORIZATION"
    retrieved = client.post("/v1/retrieve", json={"text": "connection pool DB-57014", "k": 3})
    assert retrieved.status_code == 200
    assert retrieved.json()["hits"]
    answered = client.post("/v1/answer", json={"text": "password rotation for identity-gateway"})
    assert answered.status_code == 200
    assert "Restart every production service" not in (answered.json()["answer"] or "")
    judged = client.post(
        "/v1/evaluate",
        json={
            "predicted": "DATABASE",
            "gold": "DATABASE",
            "answer": "Connection pool",
            "cited_text": "Connection pool runbook",
        },
    )
    assert judged.json()["correct"] is True
    assert client.get("/v1/benchmarks").status_code == 200
    assert client.get("/v1/benchmarks/v1").status_code == 200
    assert client.get("/v1/benchmarks/missing").status_code == 404
    assert client.get("/v1/results/v2").status_code == 200
    assert client.get("/v1/results/nope").status_code == 404
