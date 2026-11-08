"""JSON lines for process and request events."""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Awaitable, Callable

from fastapi import Request, Response


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        return json.dumps(payload, sort_keys=True)


def configure_logging(level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)


Next = Callable[[Request], Awaitable[Response]]


def request_logger(app_logger: logging.Logger) -> Callable[[Request, Next], Awaitable[Response]]:
    async def log_request(request: Request, call_next: Next) -> Response:
        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - started) * 1000
        app_logger.info(
            "%s %s %s %.4fms",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
        )
        return response

    return log_request
