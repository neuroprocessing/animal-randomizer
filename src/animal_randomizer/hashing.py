from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from typing import Any


def to_canonical_json(value: Any) -> str:
    """Serialize in a deterministic JSON format for reproducibility hashing."""

    if is_dataclass(value):
        value = asdict(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str)


def sha256_of(value: Any) -> str:
    payload = to_canonical_json(value).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
