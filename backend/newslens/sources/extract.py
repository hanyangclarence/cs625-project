"""Article body extraction via Trafilatura."""

from __future__ import annotations

from dataclasses import dataclass

import trafilatura


@dataclass
class Extracted:
    text: str
    title: str | None
    author: str | None
    published: str | None
    image: str | None
    language: str | None


def extract(html: str, url: str) -> Extracted:
    """Best-effort body extraction. Empty text means we should treat the
    article as a paywall/extraction failure."""
    body = trafilatura.extract(
        html,
        url=url,
        favor_recall=True,
        include_comments=False,
        include_tables=False,
        deduplicate=True,
    ) or ""

    meta_obj = None
    try:
        meta_obj = trafilatura.extract_metadata(html)
    except Exception:
        meta_obj = None

    def _attr(name: str) -> str | None:
        if meta_obj is None:
            return None
        v = getattr(meta_obj, name, None)
        if isinstance(v, list):
            return ", ".join(str(x) for x in v if x)
        return v

    return Extracted(
        text=body,
        title=_attr("title"),
        author=_attr("author"),
        published=_attr("date"),
        image=_attr("image"),
        language=_attr("language"),
    )
