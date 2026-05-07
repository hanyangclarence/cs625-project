"""Per-article atomic claim extraction with quote substring guard."""

from __future__ import annotations

from .. import config, llm
from ..workspaces.schema import ArticleClaim, ArticleWorkspace
from . import _prompts

MAX_PER_ARTICLE = 7


def extract(ws: ArticleWorkspace) -> ArticleWorkspace:
    if not ws.cleaned_text:
        return ws
    system = _prompts.load("claims")
    article_block = f"<article>\n{ws.cleaned_text}\n</article>"
    data = llm.call_json(
        instruction="Extract atomic claims from the article above.",
        cached_blocks=[system, article_block],
        model=config.MODEL,
        max_tokens=2048,
    )
    if not isinstance(data, list):
        return ws

    out: list[ArticleClaim] = []
    for i, item in enumerate(data[:MAX_PER_ARTICLE]):
        if not isinstance(item, dict):
            continue
        text = str(item.get("text", "")).strip()
        quote = str(item.get("quote", "")).strip()
        if not text or not quote:
            continue
        # Substring guard. Demote to drop on miss; we don't trust the claim
        # without a real anchor.
        if quote not in ws.cleaned_text:
            continue
        out.append(ArticleClaim(id=f"{ws.id}:{i}", text=text, quote=quote))

    ws.claims = out
    return ws
