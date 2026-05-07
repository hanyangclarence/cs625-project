"""End-to-end orchestrator for one topic.

Stages: discover → fetch → extract → clean → inspect → verify → claims → trust
        → align → lenses → evidence → timeline → export.

Resume mode skips fetch/extract/clean/inspect/verify when ArticleWorkspaces
already exist on disk. Useful when iterating prompts on later stages.
"""

from __future__ import annotations

import re
import time
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

from . import config
from .pipeline import (
    aligner,
    claims,
    cleaner,
    evidence as evidence_stage,
    exporter,
    inspector,
    lenses,
    timeline,
    trust,
    verifier,
)
from .sources import crawler, extract, feeds
from .workspaces import store
from .workspaces.schema import ArticleWorkspace, EventWorkspace


def _outlet_key(outlet: str, url: str) -> str:
    netloc = urlparse(url).netloc.lower().removeprefix("www.")
    base = (outlet or netloc).lower().split()[0]
    base = re.sub(r"[^a-z0-9]", "", base) or netloc.split(".")[0]
    return base


def _article_id(outlet_key: str, date_iso: str | None) -> str:
    date = (date_iso or "")[:10]
    return f"{outlet_key}-{date}" if date else outlet_key


def _domain(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


def discover_articles(
    *,
    topic: str,
    topic_id: str,
    max_sources: int,
) -> list[ArticleWorkspace]:
    """Stage A: discover, fetch, extract. Returns provisional workspaces with
    raw_text populated. Drops paywalled/empty articles."""
    candidates = feeds.discover(topic, topic_id, max_items=max_sources * 3)
    if not candidates:
        return []
    fetched = crawler.fetch_all(candidates)

    out: list[ArticleWorkspace] = []
    seen_keys: set[str] = set()
    for item, html in fetched:
        if len(out) >= max_sources:
            break
        ext = extract.extract(html, item.url)
        if not ext.text or len(ext.text) < 250:
            continue
        outlet_key = _outlet_key(item.outlet, item.url)
        # Dedup: one article per outlet — pick the first non-stub.
        if outlet_key in seen_keys:
            continue
        seen_keys.add(outlet_key)

        ws = ArticleWorkspace(
            id=_article_id(outlet_key, ext.published or item.published_at),
            url=item.url,
            outlet=item.outlet,
            outlet_domain=_domain(item.url),
            title=ext.title or item.title or item.outlet,
            author=ext.author,
            published_at=ext.published or item.published_at,
            image_url=ext.image,
            raw_text=ext.text,
        )
        out.append(ws)
    return out


def process_article(ws: ArticleWorkspace, *, verify: bool = False) -> ArticleWorkspace:
    """Stage B: clean → inspect → (verify) → claims → trust."""
    cleaned = cleaner.clean(ws.raw_text)
    if not cleaned:
        ws.validity_notes.append("paywalled or unrecoverable; skipped")
        return ws
    ws.cleaned_text = cleaned
    fallback_date = ws.published_at
    ws = inspector.inspect(ws, fallback_date=fallback_date)
    if verify:
        ws = verifier.verify(ws)
    else:
        ws.validity_notes.append("verifier skipped (--no-verify)")
    ws = claims.extract(ws)
    ws = trust.score(ws)
    return ws


def build_event(
    *,
    topic: str,
    topic_id: str,
    articles: list[ArticleWorkspace],
) -> EventWorkspace:
    """Stage C: align → lenses → evidence → timeline."""
    canonical = aligner.align(articles)
    lens_map = lenses.assign(articles, canonical)
    evidence_index = evidence_stage.map_evidence(articles, canonical)
    timeline_index = timeline.build(articles, canonical)

    return EventWorkspace(
        topic_id=topic_id,
        title=topic,
        article_ids=[ws.id for ws in articles if ws.cleaned_text],
        canonical_claims=canonical,
        lenses=lens_map,
        evidence_index=evidence_index,
        timeline_index=timeline_index,
    )


def run(
    *,
    topic: str,
    topic_id: str,
    max_sources: int = 3,
    out_path: Path | None = None,
    resume: bool = False,
    verify: bool = False,
    on_progress: Callable[[str], None] | None = None,
) -> Path:
    started = time.time()
    out_path = Path(out_path) if out_path else (config.PUBLIC_DATA_DIR / f"{topic_id}.json")

    def log(line: str) -> None:
        print(line, flush=True)
        if on_progress:
            try:
                on_progress(line)
            except Exception:
                pass

    if resume:
        articles = store.list_articles(topic_id)
        articles = [a for a in articles if a.cleaned_text]
        if not articles:
            raise RuntimeError(
                f"--resume requested but no processed workspaces found under "
                f"{config.WORKSPACES_DIR / topic_id}"
            )
    else:
        log(f"[discover] querying feeds for {topic!r}...")
        provisional = discover_articles(
            topic=topic, topic_id=topic_id, max_sources=max_sources
        )
        if not provisional:
            raise RuntimeError("no candidate articles found")
        log(f"[discover] {len(provisional)} candidate articles fetched")

        articles = []
        for ws in provisional:
            log(f"[process] {ws.id} ({ws.outlet}){' [no-verify]' if not verify else ''}")
            ws = process_article(ws, verify=verify)
            store.save_article(topic_id, ws)
            if ws.cleaned_text and ws.trust:
                articles.append(ws)

    if not articles:
        raise RuntimeError("no articles survived processing")

    log(f"[event] aligning {len(articles)} articles...")
    event = build_event(topic=topic, topic_id=topic_id, articles=articles)
    store.save_event(event)

    log(f"[export] assembling Topic JSON to {out_path}")
    topic_obj = exporter.assemble(event=event, articles=articles)
    exporter.write(topic_obj, out_path)

    store.write_meta(
        topic_id,
        {
            "topic": topic,
            "topic_id": topic_id,
            "elapsed_seconds": round(time.time() - started, 2),
            "article_count": len(articles),
            "claim_count": len(topic_obj.claims),
            "timeline_count": len(topic_obj.timeline),
            "out_path": str(out_path),
        },
    )

    log(
        f"[done] {len(topic_obj.sources)} sources, "
        f"{len(topic_obj.claims)} claims, "
        f"{len(topic_obj.timeline)} timeline entries — "
        f"{time.time() - started:.1f}s"
    )
    return out_path
