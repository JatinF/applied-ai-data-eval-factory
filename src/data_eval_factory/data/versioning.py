from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_hash(payload: Any) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def split_for(sample_id: str) -> str:
    bucket = int(hashlib.sha256(sample_id.encode("utf-8")).hexdigest()[:8], 16) % 10
    if bucket < 6:
        return "train"
    if bucket < 8:
        return "validation"
    return "test"
