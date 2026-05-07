"""Build the per-claim reporting timeline.

For each canonical claim:
  1. Collect (date, source, supporting passage) tuples from articles whose
     own claims align under that canonical id.
  2. Sort chronologically.
  3. Ask the LLM to label each entry as Appears / Picked up / Supplemented and
     write a short note.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

from .. import config, llm
from ..workspaces.schema import (
    ArticleWorkspace,
    CanonicalClaim,
    TimelineItem,
    TimelineStage,
)
from . import _prompts

_STAGES: tuple[TimelineStage, ...] = ("Appears", "Picked up", "Supplemented")


def _short_date(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(timezone.utc).date().isoformat()
    except Exception:
        return iso[:10]


def build(
    articles: list[ArticleWorkspace],
    canonical_claims: list[CanonicalClaim],
) -> list[TimelineItem]:
    out: list[TimelineItem] = []
    by_id = {ws.id: ws for ws in articles}

    system = _prompts.load("timeline")

    for claim in canonical_claims:
        # Collect article-claim refs that match this canonical, with quote.
        rows = []
        for ref in claim.article_claim_refs:
            article_id, _, idx_str = ref.partition(":")
            ws = by_id.get(article_id)
            if not ws:
                continue
            try:
                idx = int(idx_str)
            except ValueError:
                continue
            if idx < 0 or idx >= len(ws.claims):
                continue
            quote = ws.claims[idx].quote
            rows.append(
                {
                    "source_id": ws.id,
                    "date": _short_date(ws.published_at),
                    "passage": quote,
                }
            )
        if not rows:
            continue
        rows.sort(key=lambda r: r["date"])

        claim_block = (
            "<claim>\n"
            + json.dumps({"id": claim.id, "text": claim.text}, ensure_ascii=False)
            + "\n</claim>"
        )
        rows_block = (
            "<entries>\n"
            + json.dumps(
                [{"index": i, **r} for i, r in enumerate(rows)],
                ensure_ascii=False,
            )
            + "\n</entries>"
        )

        data = llm.call_json(
            instruction="Label each entry per the rubric above.",
            cached_blocks=[system, claim_block, rows_block],
            model=config.MODEL,
            max_tokens=1024,
        )

        labels: dict[int, dict] = {}
        if isinstance(data, dict):
            for item in data.get("entries", []) or []:
                if not isinstance(item, dict):
                    continue
                try:
                    idx = int(item.get("index", -1))
                except Exception:
                    continue
                stage = item.get("stage")
                if stage not in _STAGES:
                    continue
                labels[idx] = {
                    "stage": stage,
                    "shortNote": str(item.get("shortNote", "")).strip() or None,
                }

        for i, r in enumerate(rows):
            label = labels.get(i)
            if not label:
                # Default: first entry is Appears, rest Picked up.
                stage = "Appears" if i == 0 else "Picked up"
                short_note = None
            else:
                stage = label["stage"]
                short_note = label["shortNote"]
            out.append(
                TimelineItem(
                    date=r["date"] or "",
                    sourceId=r["source_id"],
                    claimId=claim.id,
                    stage=stage,
                    shortNote=short_note,
                )
            )

    out.sort(key=lambda i: (i.date, i.sourceId))
    return out
