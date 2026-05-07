"""Content-hash disk cache for LLM responses.

Keyed on sha256 of (model + serialized request). Stored as JSON files under
.cache/llm/. Re-running the same prompt is a no-op API call.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from . import config


def _cache_path(key: str) -> Path:
    config.CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return config.CACHE_DIR / f"{key}.json"


def make_key(payload: dict[str, Any]) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def get(key: str) -> dict[str, Any] | None:
    path = _cache_path(key)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def put(key: str, value: dict[str, Any]) -> None:
    path = _cache_path(key)
    path.write_text(json.dumps(value, indent=2, default=str))
