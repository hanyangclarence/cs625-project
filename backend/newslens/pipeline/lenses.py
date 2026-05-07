"""Per-source matchTag + matchScore against the canonical claim set."""

from __future__ import annotations

import json

from .. import config, llm
from ..workspaces.schema import ArticleWorkspace, CanonicalClaim, LensTag
from . import _prompts

_VALID = {"shared-facts", "framing-gaps", "evidence-support"}


def assign(
    articles: list[ArticleWorkspace],
    canonical_claims: list[CanonicalClaim],
) -> dict[str, LensTag]:
    if not canonical_claims:
        return {}

    canonical_block = (
        "<canonical_claims>\n"
        + json.dumps(
            [{"id": c.id, "text": c.text} for c in canonical_claims],
            ensure_ascii=False,
        )
        + "\n</canonical_claims>"
    )

    # Per-source: which canonicals it addresses + a snippet for framing tone.
    coverage = []
    for ws in articles:
        covered = [
            c.id
            for c in canonical_claims
            if any(ref.startswith(ws.id + ":") for ref in c.article_claim_refs)
        ]
        snippet = (ws.cleaned_text or "")[:1200]
        coverage.append(
            {
                "source_id": ws.id,
                "outlet": ws.outlet,
                "covers": covered,
                "snippet": snippet,
            }
        )

    sources_block = "<sources>\n" + json.dumps(coverage, ensure_ascii=False) + "\n</sources>"

    system = _prompts.load("lenses")
    data = llm.call_json(
        instruction="Tag each source per the rubric above.",
        cached_blocks=[system, canonical_block, sources_block],
        model=config.MODEL,
        max_tokens=2048,
    )

    raw = data.get("lenses") if isinstance(data, dict) else None
    if not isinstance(raw, dict):
        return {}

    out: dict[str, LensTag] = {}
    for source_id, item in raw.items():
        if not isinstance(item, dict):
            continue
        tag = item.get("matchTag")
        if tag not in _VALID:
            continue
        try:
            score = int(item.get("matchScore", 0))
        except Exception:
            score = 0
        score = max(0, min(100, score))
        out[source_id] = LensTag(matchTag=tag, matchScore=score)
    return out
