"""Cross-source claim alignment.

Inputs: all ArticleWorkspaces with their per-article claims.
Output: a list of CanonicalClaim with article_claim_refs back-pointers.
"""

from __future__ import annotations

import json
import re

from .. import config, llm
from ..workspaces.schema import ArticleWorkspace, CanonicalClaim
from . import _prompts


def _slug(s: str, fallback: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    s = re.sub(r"-+", "-", s)
    return ("c-" + s)[:48] or fallback


def align(articles: list[ArticleWorkspace]) -> list[CanonicalClaim]:
    pairs: list[dict] = []
    for ws in articles:
        for c in ws.claims:
            pairs.append({"id": c.id, "text": c.text})

    if not pairs:
        return []

    system = _prompts.load("aligner")
    payload_block = f"<input_claims>\n{json.dumps(pairs, ensure_ascii=False)}\n</input_claims>"
    data = llm.call_json(
        instruction="Align the input_claims above into canonical claims.",
        cached_blocks=[system, payload_block],
        model=config.MODEL,
        max_tokens=4096,
    )

    raw_canon = data.get("canonical_claims") if isinstance(data, dict) else data
    if not isinstance(raw_canon, list):
        return []

    used_ids: set[str] = set()
    out: list[CanonicalClaim] = []
    for i, c in enumerate(raw_canon):
        if not isinstance(c, dict):
            continue
        text = str(c.get("text", "")).strip()
        if not text:
            continue
        refs = [str(r) for r in (c.get("article_claim_refs") or []) if r]
        if not refs:
            continue
        cid = str(c.get("id", "")).strip() or _slug(text, f"c-{i}")
        # Make sure ids are unique.
        base = cid
        n = 2
        while cid in used_ids:
            cid = f"{base}-{n}"
            n += 1
        used_ids.add(cid)
        out.append(CanonicalClaim(id=cid, text=text, article_claim_refs=refs))

    return out
