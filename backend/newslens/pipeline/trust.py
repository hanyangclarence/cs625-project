"""Trust scoring.

Three rubric components, each capped at 30. Sum = trustScore (0..90 mapped to
0..100 by clipping). trustLabel via derive_trust_label (>60 / >=30 / else).

  - references: rule-based — count of resolved references (capped). Articles
    with named refs and at least one URL get the most credit.
  - authority: rule-based — outlet allowlist + tld + has-author.
  - clarity: LLM rubric (one fast call).
"""

from __future__ import annotations

from urllib.parse import urlparse

from .. import config, llm
from ..workspaces.schema import ArticleWorkspace, Rubric, TrustBlock
from . import _prompts

REPUTABLE_DOMAINS = {
    "nasa.gov", "nytimes.com", "apnews.com", "reuters.com", "bbc.com", "bbc.co.uk",
    "theguardian.com", "guardian.co.uk", "npr.org", "washingtonpost.com",
    "wsj.com", "bloomberg.com", "ft.com", "economist.com", "nature.com",
    "science.org", "scientificamerican.com", "wired.com", "theverge.com",
    "arstechnica.com", "spacenews.com", "space.com", "noaa.gov", "nih.gov",
}
TRUSTED_TLDS = {"gov", "edu", "mil"}


def _references_score(ws: ArticleWorkspace) -> int:
    refs = ws.references
    if not refs:
        return 8
    count = len(refs)
    with_url = sum(1 for r in refs if r.url)
    # Up to 30. Saturating.
    score = min(30, 10 + min(count, 6) * 3 + min(with_url, 4) * 2)
    return score


def _authority_score(ws: ArticleWorkspace) -> int:
    base = 14
    domain = (ws.outlet_domain or "").lower()
    if domain in REPUTABLE_DOMAINS:
        base += 10
    tld = domain.rsplit(".", 1)[-1] if domain else ""
    if tld in TRUSTED_TLDS:
        base += 4
    if ws.author:
        base += 2
    return min(30, base)


def _clarity_score(ws: ArticleWorkspace) -> int:
    if not ws.cleaned_text:
        return 0
    system = _prompts.load("trust_clarity")
    article_block = f"<article>\n{ws.cleaned_text}\n</article>"
    data = llm.call_json(
        instruction="Score clarity per the rubric above.",
        cached_blocks=[system, article_block],
        model=config.MODEL_FAST,
        max_tokens=512,
    )
    try:
        v = int(data["clarity"]) if isinstance(data, dict) else 0
    except Exception:
        v = 0
    return max(0, min(30, v))


def score(ws: ArticleWorkspace) -> ArticleWorkspace:
    rubric = Rubric(
        references=_references_score(ws),
        authority=_authority_score(ws),
        clarity=_clarity_score(ws),
    )
    total = rubric.references + rubric.authority + rubric.clarity  # 0..90
    # Map to 0..100 by saturating at 90.
    trust_score = min(100, int(round(total * 100 / 90)))
    ws.trust = TrustBlock(rubric=rubric, trustScore=trust_score)
    return ws


def domain_for(url: str) -> str:
    try:
        netloc = urlparse(url).netloc.lower()
    except Exception:
        return ""
    return netloc.removeprefix("www.")
