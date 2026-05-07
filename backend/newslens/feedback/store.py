"""Append-only JSONL storage for user signals and expert audit labels."""

from __future__ import annotations

import json
import time
from pathlib import Path

from .. import config


def _file(kind: str, topic_id: str) -> Path:
    base = config.FEEDBACK_DIR / kind
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{topic_id}.jsonl"


def append_signal(topic_id: str, payload: dict) -> Path:
    return _append("signals", topic_id, payload)


def append_audit(topic_id: str, payload: dict) -> Path:
    return _append("audit", topic_id, payload)


def _append(kind: str, topic_id: str, payload: dict) -> Path:
    record = {"ts": time.time(), **payload}
    path = _file(kind, topic_id)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    return path


def read(kind: str, topic_id: str) -> list[dict]:
    path = _file(kind, topic_id)
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out
