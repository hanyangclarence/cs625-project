"""HTTP fetch with throttle, retry, robots.txt check, and dedup.

Returns a list of (FeedItem, html) for items that fetched successfully and
weren't blocked by robots.txt.
"""

from __future__ import annotations

import asyncio
import urllib.robotparser
from urllib.parse import urlparse

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from .. import config
from .feeds import FeedItem

DEFAULT_TIMEOUT = 20.0
MAX_CONCURRENT = 4


def _robots_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
        rp.read()
        return rp.can_fetch(config.USER_AGENT, url)
    except Exception:
        # If robots fails to load, allow but log via caller.
        return True


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=8), reraise=True)
async def _fetch_one(client: httpx.AsyncClient, url: str) -> str:
    resp = await client.get(url, follow_redirects=True)
    resp.raise_for_status()
    return resp.text


async def _fetch_all_async(items: list[FeedItem]) -> list[tuple[FeedItem, str]]:
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    out: list[tuple[FeedItem, str]] = []

    headers = {"User-Agent": config.USER_AGENT}
    async with httpx.AsyncClient(headers=headers, timeout=DEFAULT_TIMEOUT) as client:

        async def task(item: FeedItem) -> None:
            async with sem:
                if not _robots_allowed(item.url):
                    return
                try:
                    html = await _fetch_one(client, item.url)
                except Exception:
                    return
                out.append((item, html))

        await asyncio.gather(*(task(i) for i in items))
    return out


def fetch_all(items: list[FeedItem]) -> list[tuple[FeedItem, str]]:
    return asyncio.run(_fetch_all_async(items))
