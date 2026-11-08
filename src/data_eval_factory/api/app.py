from __future__ import annotations

import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from data_eval_factory import __version__
from data_eval_factory.evaluation.groundedness import groundedness
from data_eval_factory.evaluation.runner import Runtime, execute
from data_eval_factory.log import request_logger
from data_eval_factory.models.prompt_model import answer_prompt
from data_eval_factory.retrieval.retriever import search


class PredictRequest(BaseModel):
    text: str
    service: str = "unknown"
    severity: str = "P3"
    error_codes: list[str] = Field(default_factory=list)
    product: str = "unknown"
    k: int = 5


class EvaluateRequest(BaseModel):
    predicted: str | None
    gold: str
    answer: str | None = None
    cited_text: str = ""


def create_app(runtime: Runtime | None = None) -> FastAPI:
    resolved = runtime or execute()
    app = FastAPI(title="Applied AI Data Eval Factory", version=__version__)
    app.state.runtime = resolved
    app.middleware("http")(request_logger(logging.getLogger("data_eval_factory.api")))

    @app.get("/health")
    def health() -> dict[str, str]:
        return {
            "status": "ok",
            "version": __version__,
            "hosted_llm": resolved.report.hosted_llm,
            "lora": resolved.report.lora,
        }

    @app.post("/v1/classify")
    def classify(body: PredictRequest) -> dict[str, object]:
        label, confidence = resolved.linear.predict(body.text, body.service, body.error_codes)
        return {"label": label, "confidence": confidence, "model": "linear_finetune"}

    @app.post("/v1/retrieve")
    def retrieve(body: PredictRequest) -> dict[str, object]:
        hits = search(resolved.index, body.text, k=body.k)
        return {
            "hits": [
                {
                    "id": hit.document.id,
                    "title": hit.document.title,
                    "category": hit.document.category,
                    "score": hit.score,
                }
                for hit in hits
            ]
        }

    @app.post("/v1/answer")
    def answer(body: PredictRequest) -> dict[str, object]:
        hits = search(resolved.index, body.text, k=body.k)
        text, citations = answer_prompt(hits, strip_unsupported=True)
        label, confidence = resolved.linear.predict(body.text, body.service, body.error_codes)
        return {"label": label, "confidence": confidence, "answer": text, "citations": citations}

    @app.post("/v1/evaluate")
    def evaluate(body: EvaluateRequest) -> dict[str, object]:
        return {
            "correct": body.predicted == body.gold,
            "groundedness": groundedness(body.answer, body.cited_text),
        }

    @app.get("/v1/benchmarks")
    def benchmarks() -> list[dict[str, object]]:
        return [item.model_dump() for item in resolved.report.manifests]

    @app.get("/v1/benchmarks/{version}")
    def benchmark(version: str) -> dict[str, object]:
        for item in resolved.report.manifests:
            if item.version == version:
                return item.model_dump()
        raise HTTPException(status_code=404, detail="benchmark not found")

    @app.get("/v1/results/{run_id}")
    def results(run_id: str) -> dict[str, object]:
        if run_id == "v1":
            return resolved.report.v1.model_dump()
        if run_id == "v2":
            return resolved.report.v2.model_dump()
        raise HTTPException(status_code=404, detail="run not found")

    return app
