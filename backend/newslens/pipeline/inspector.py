"""Extract author, publication date, references, and a short summary.

Combines an LLM JSON-mode call with a `dateparser` fallback for the date.
"""

from __future__ import annotations

from datetime import datetime, timezone

import dateparser

from .. import config, llm
from ..workspaces.schema import ArticleWorkspace, Reference
from . import _prompts


def _normalize_date(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        dt = dateparser.parse(
            raw,
            settings={"TIMEZONE": "UTC", "RETURN_AS_TIMEZONE_AWARE": True},
        )
    except Exception:
        dt = None
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat()


def inspect(ws: ArticleWorkspace, *, fallback_date: str | None) -> ArticleWorkspace:
    """Mutates and returns ws with author/date/refs/summary populated."""
    if not ws.cleaned_text:
        return ws

    system = _prompts.load("inspector")
    article_block = (
        f"<article>\noutlet={ws.outlet}\nurl={ws.url}\n\n{ws.cleaned_text}\n</article>"
    )
    data = llm.call_json(
        instruction="Extract metadata for the article above.",
        cached_blocks=[system, article_block],
        model=config.MODEL_FAST,
        max_tokens=2048,
    )

    if isinstance(data, dict):
        ws.author = (data.get("author") or None) or ws.author
        candidate = data.get("published_at") or fallback_date
        ws.published_at = _normalize_date(candidate) or ws.published_at or _normalize_date(fallback_date)
        ws.summary = (data.get("summary") or "").strip() or ws.summary
        refs = data.get("references") or []
        if isinstance(refs, list):
            ws.references = [
                Reference(
                    text=str(r.get("text", "")).strip(),
                    url=(r.get("url") or None),
                )
                for r in refs
                if isinstance(r, dict) and str(r.get("text", "")).strip()
            ][:8]

    if not ws.published_at:
        # Last-ditch: today's date so downstream timeline ordering doesn't NaN.
        ws.published_at = datetime.now(timezone.utc).isoformat()
        ws.validity_notes.append("published_at fell back to crawl time (no date found)")

    return ws
