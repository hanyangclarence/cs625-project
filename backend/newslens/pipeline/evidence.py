"""For each canonical claim × article, find the best supporting passage.

Includes a substring guard (we drop anything the model paraphrased) and a
demotion rule for weak/empty support.
"""

from __future__ import annotations

import json

from .. import config, llm
from ..workspaces.schema import (
    ArticleWorkspace,
    CanonicalClaim,
    EvidenceItem,
    SupportLevel,
)
from . import _prompts

_VALID_LEVELS: tuple[SupportLevel, ...] = ("strong", "partial", "weaker")


def map_evidence(
    articles: list[ArticleWorkspace],
    canonical_claims: list[CanonicalClaim],
) -> dict[str, list[EvidenceItem]]:
    by_claim: dict[str, list[EvidenceItem]] = {}
    system = _prompts.load("evidence")

    for claim in canonical_claims:
        items: list[EvidenceItem] = []
        claim_block = (
            "<claim>\n"
            + json.dumps({"id": claim.id, "text": claim.text}, ensure_ascii=False)
            + "\n</claim>"
        )
        for ws in articles:
            if not ws.cleaned_text:
                continue
            article_block = (
                f"<article id='{ws.id}'>\n{ws.cleaned_text}\n</article>"
            )
            data = llm.call_json(
                instruction="Find the best supporting passage in the article.",
                cached_blocks=[system, claim_block, article_block],
                model=config.MODEL,
                max_tokens=1024,
            )
            if not isinstance(data, dict):
                continue
            passage = str(data.get("passage", "")).strip()
            if not passage:
                continue
            # Substring guard.
            if passage not in ws.cleaned_text:
                continue
            level = data.get("supportLevel", "weaker")
            if level not in _VALID_LEVELS:
                level = "weaker"
            try:
                score = int(data.get("score", 0))
            except Exception:
                score = 0
            score = max(0, min(100, score))
            items.append(
                EvidenceItem(
                    sourceId=ws.id,
                    passage=passage,
                    supportLevel=level,
                    score=score,
                )
            )
        # Sort by score desc; cap at 6 to avoid runaway lists.
        items.sort(key=lambda i: i.score, reverse=True)
        by_claim[claim.id] = items[:6]

    return by_claim
