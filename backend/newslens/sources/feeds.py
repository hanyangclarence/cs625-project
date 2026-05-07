"""Source discovery: candidate URLs for a topic.

Two strategies blend together:
  1. Curated allowlist — per-topic seed feeds for outlets we know cover the
     story. For Artemis II we seed NASA, AP, the Guardian, and NPR so demo
     output mirrors the hand-authored dataset.
  2. Google News RSS — a broad query for the topic, scoped to recent items.

Both return iterables of (url, outlet, published_at). Higher up the pipeline
deduplicates and caps the article count.
"""

from __future__ import annotations

import base64
import urllib.parse
from dataclasses import dataclass
from datetime import datetime, timezone

import feedparser
import tldextract


@dataclass
class FeedItem:
    url: str
    outlet: str
    title: str
    published_at: str | None  # ISO 8601 if known


CURATED: dict[str, list[tuple[str, str]]] = {
    # topic-id -> list of (feed_url, outlet_label)
    "artemis-ii-lunar-flyby": [
        # NASA Artemis blog
        ("https://www.nasa.gov/feeds/iotd-feed/", "NASA"),
        # AP space hub
        ("https://apnews.com/hub/space/feed", "AP News"),
        # Guardian science/space
        ("https://www.theguardian.com/science/space/rss", "The Guardian"),
        # NPR space
        ("https://feeds.npr.org/1007/rss.xml", "NPR"),
    ],
}


def _outlet_label_from_url(url: str) -> str:
    ext = tldextract.extract(url)
    return ext.domain.upper() if ext.domain else url


def _parse_date(entry) -> str | None:
    for key in ("published_parsed", "updated_parsed"):
        v = getattr(entry, key, None) or entry.get(key) if isinstance(entry, dict) else None
        if v:
            try:
                return datetime(*v[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    raw = entry.get("published") if isinstance(entry, dict) else getattr(entry, "published", None)
    return raw if raw else None


def google_news_query(topic: str, when_days: int = 30) -> str:
    q = urllib.parse.quote_plus(f"{topic} when:{when_days}d")
    return f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"


def bing_news_query(topic: str) -> str:
    q = urllib.parse.quote_plus(topic)
    return f"https://www.bing.com/news/search?q={q}&format=rss&cc=US"


def _resolve_bing_link(link: str) -> str:
    """Bing wraps article URLs in apiclick.aspx?...&url=<real>. Extract the real URL."""
    try:
        qs = urllib.parse.urlparse(link).query
        params = urllib.parse.parse_qs(qs)
        raw = params.get("url", [""])[0]
        if not raw:
            return link
        if raw.startswith("http"):
            return raw
        try:
            return base64.b64decode(raw + "===").decode("utf-8", errors="ignore") or link
        except Exception:
            return link
    except Exception:
        return link


def discover(topic: str, topic_id: str, max_items: int = 24) -> list[FeedItem]:
    """Pull candidate articles for the topic. Returns up to max_items.

    Curated seeds first (ordered), then Google News RSS to fill remaining slots.
    """
    seen: set[str] = set()
    items: list[FeedItem] = []

    def absorb(url: str, outlet: str, title: str, published: str | None) -> None:
        if not url or url in seen:
            return
        seen.add(url)
        items.append(FeedItem(url=url, outlet=outlet, title=title, published_at=published))

    for feed_url, outlet in CURATED.get(topic_id, []):
        if len(items) >= max_items:
            break
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            continue
        for entry in (feed.entries or [])[:8]:
            link = (entry.get("link") if isinstance(entry, dict) else None) or getattr(
                entry, "link", ""
            )
            title = (entry.get("title") if isinstance(entry, dict) else None) or getattr(
                entry, "title", ""
            )
            absorb(link, outlet, title, _parse_date(entry))

    if len(items) < max_items:
        # Bing News RSS exposes article URLs in a query param (vs Google News
        # which wraps them in JS-redirect tokens that can't be fetched directly).
        feed = feedparser.parse(bing_news_query(topic))
        for entry in (feed.entries or []):
            if len(items) >= max_items:
                break
            wrapper = entry.get("link") if isinstance(entry, dict) else getattr(entry, "link", "")
            link = _resolve_bing_link(wrapper)
            title = entry.get("title") if isinstance(entry, dict) else getattr(entry, "title", "")
            outlet = _outlet_label_from_url(link)
            absorb(link, outlet, title, _parse_date(entry))

    return items
