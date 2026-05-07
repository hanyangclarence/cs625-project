"""Strip boilerplate from an article body.

Returns the cleaned text. Returns "" if the article looks paywalled.
"""

from __future__ import annotations

from .. import config, llm
from . import _prompts


PAYWALL_TOKEN = "PAYWALLED"


def clean(raw_text: str) -> str:
    if not raw_text or len(raw_text) < 200:
        return ""
    system = _prompts.load("cleaner")
    article_block = f"<article>\n{raw_text}\n</article>"
    out = llm.call_text(
        instruction="Clean the article above per the rules.",
        cached_blocks=[system, article_block],
        model=config.MODEL_FAST,
        max_tokens=8192,
    ).strip()
    if out.strip() == PAYWALL_TOKEN:
        return ""
    return out
