from __future__ import annotations

import re

TOKEN = re.compile(r"[a-z0-9]+")


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def tokenize(text: str) -> list[str]:
    return TOKEN.findall(text.lower())
