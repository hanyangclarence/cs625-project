"""Assemble the frontend-facing Topic JSON from workspaces.

Validates every invariant from src/types/news.ts before writing:
  - id-link integrity (EvidenceLink.sourceId, TimelineEntry.sourceId/claimId)
  - trustLabel === deriveTrustLabel(trustScore)
  - rubric components in [0, 30]
  - every EvidenceLink.passage is a substring of the source article's cleaned_text
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from ..workspaces.schema import (
    ArticleWorkspace,
    Claim,
    EventWorkspace,
    EvidenceLink,
    Source,
    TimelineEntry,
    Topic,
    derive_trust_label,
)


class ExportError(RuntimeError):
    pass


def _short_date(iso: str | None) -> str:
    if not iso:
        return ""
    try:
        return (
            datetime.fromisoformat(iso.replace("Z", "+00:00"))
            .astimezone(timezone.utc)
            .date()
            .isoformat()
        )
    except Exception:
        return iso[:10]


def assemble(
    *,
    event: EventWorkspace,
    articles: list[ArticleWorkspace],
) -> Topic:
    article_by_id = {ws.id: ws for ws in articles}
    sources: list[Source] = []
    for ws in articles:
        if not ws.cleaned_text or ws.trust is None:
            continue
        lens = event.lenses.get(ws.id)
        if lens is None:
            # Source had no lens assigned; skip — it can't render in cross-source view.
            continue
        trust_score = ws.trust.trustScore
        sources.append(
            Source(
                id=ws.id,
                outlet=ws.outlet,
                date=_short_date(ws.published_at),
                articleTitle=ws.title or ws.outlet,
                url=ws.url or None,
                imageUrl=ws.image_url,
                matchTag=lens.matchTag,
                matchScore=lens.matchScore,
                trustScore=trust_score,
                trustLabel=derive_trust_label(trust_score),
                summary=ws.summary or "",
                rubric=ws.trust.rubric,
            )
        )
    source_ids = {s.id for s in sources}

    claims: list[Claim] = []
    for canon in event.canonical_claims:
        items = event.evidence_index.get(canon.id, [])
        evidence: list[EvidenceLink] = []
        for it in items:
            if it.sourceId not in source_ids:
                continue
            evidence.append(
                EvidenceLink(
                    sourceId=it.sourceId,
                    passage=it.passage,
                    supportLevel=it.supportLevel,
                    score=it.score,
                )
            )
        if not evidence:
            continue
        avg = sum(e.score for e in evidence) / len(evidence)
        claims.append(
            Claim(
                id=canon.id,
                text=canon.text,
                overallTrust=derive_trust_label(int(round(avg))),
                evidence=evidence,
            )
        )
    claim_ids = {c.id for c in claims}

    timeline: list[TimelineEntry] = []
    for i, t in enumerate(event.timeline_index):
        if t.sourceId not in source_ids:
            continue
        if t.claimId and t.claimId not in claim_ids:
            continue
        timeline.append(
            TimelineEntry(
                id=f"t-{i+1}",
                date=t.date,
                sourceId=t.sourceId,
                stage=t.stage,
                shortNote=t.shortNote,
                claimId=t.claimId,
            )
        )

    topic = Topic(
        id=event.topic_id,
        title=event.title,
        sources=sources,
        claims=claims,
        timeline=timeline,
    )
    _assert_invariants(topic, articles=article_by_id)
    return topic


def _assert_invariants(topic: Topic, *, articles: dict[str, ArticleWorkspace]) -> None:
    source_ids = {s.id for s in topic.sources}
    claim_ids = {c.id for c in topic.claims}

    for s in topic.sources:
        if derive_trust_label(s.trustScore) != s.trustLabel:
            raise ExportError(
                f"trustLabel mismatch on source {s.id}: "
                f"score={s.trustScore} expected={derive_trust_label(s.trustScore)} got={s.trustLabel}"
            )
        for fname, val in (
            ("references", s.rubric.references),
            ("authority", s.rubric.authority),
            ("clarity", s.rubric.clarity),
        ):
            if not (0 <= val <= 30):
                raise ExportError(f"rubric.{fname} out of range on {s.id}: {val}")

    for c in topic.claims:
        if not c.evidence:
            raise ExportError(f"claim {c.id} has no evidence")
        for e in c.evidence:
            if e.sourceId not in source_ids:
                raise ExportError(
                    f"claim {c.id} evidence references unknown sourceId {e.sourceId}"
                )
            ws = articles.get(e.sourceId)
            if ws and e.passage not in (ws.cleaned_text or ""):
                raise ExportError(
                    f"claim {c.id} passage from {e.sourceId} is not a substring of cleaned_text"
                )

    for t in topic.timeline:
        if t.sourceId not in source_ids:
            raise ExportError(f"timeline entry {t.id} references unknown sourceId {t.sourceId}")
        if t.claimId and t.claimId not in claim_ids:
            raise ExportError(f"timeline entry {t.id} references unknown claimId {t.claimId}")


def write(topic: Topic, out_path: Path) -> Path:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(topic.model_dump(), indent=2, ensure_ascii=False))
    return out_path
