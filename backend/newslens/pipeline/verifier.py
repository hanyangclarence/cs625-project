"""ReAct-style verifier loop for one ArticleWorkspace.

Tools:
  - web_search (Anthropic server tool — Anthropic executes it).
  - fetch_url (client-side tool — we run httpx + Trafilatura).

The model is instructed to confirm/contradict ~3 load-bearing claims and to
fill missing author/date. We persist its eval log onto the workspace.
"""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from .. import config, llm
from ..sources.extract import extract as extract_body
from ..workspaces.schema import ArticleWorkspace, VerifiedPassage
from . import _prompts

WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 5,
}
FETCH_URL_TOOL = {
    "name": "fetch_url",
    "description": "Fetch the cleaned body text of a URL. Returns up to ~6000 chars of plain text.",
    "input_schema": {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"],
    },
}


def _fetch_url_runner(name: str, payload: dict[str, Any]) -> str:
    if name != "fetch_url":
        return f"ERROR: unknown tool {name}"
    url = (payload or {}).get("url", "")
    if not url:
        return "ERROR: missing url"
    try:
        with httpx.Client(
            headers={"User-Agent": config.USER_AGENT},
            follow_redirects=True,
            timeout=20.0,
        ) as client:
            resp = client.get(url)
            resp.raise_for_status()
            html = resp.text
    except Exception as exc:  # noqa: BLE001
        return f"ERROR fetching {url}: {exc!s}"
    body = extract_body(html, url).text or ""
    return body[:6000] if body else "(no extractable body)"


def _strip_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\n", "", s)
        s = re.sub(r"\n```$", "", s)
    return s.strip()


def _parse_json(raw: str) -> dict[str, Any] | None:
    cleaned = _strip_fence(raw)
    try:
        return json.loads(cleaned)
    except Exception:
        m = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:
            return None


def verify(ws: ArticleWorkspace) -> ArticleWorkspace:
    if not ws.cleaned_text:
        ws.validity_notes.append("verifier skipped: no cleaned_text")
        return ws

    system_prompt = _prompts.load("verifier")
    article_block = (
        f"<article>\n"
        f"id={ws.id}\n"
        f"outlet={ws.outlet}\n"
        f"url={ws.url}\n"
        f"current_author={ws.author or 'null'}\n"
        f"current_published_at={ws.published_at or 'null'}\n\n"
        f"{ws.cleaned_text}\n"
        f"</article>"
    )

    final_text, evlog = llm.call_with_tools(
        instruction="Verify the article above. Return the JSON described in the system prompt.",
        tools=[WEB_SEARCH_TOOL, FETCH_URL_TOOL],
        tool_runner=_fetch_url_runner,
        cached_blocks=[system_prompt, article_block],
        model=config.MODEL,
        max_tool_calls=6,
        max_tokens=4096,
        temperature=0.1,
    )

    ws.eval_log.extend(evlog)
    parsed = _parse_json(final_text)
    if not parsed:
        ws.validity_notes.append("verifier returned non-JSON; kept extracted metadata")
        return ws

    if isinstance(parsed.get("author"), str) and parsed["author"].strip():
        ws.author = parsed["author"].strip()
    if isinstance(parsed.get("published_at"), str) and parsed["published_at"].strip():
        ws.published_at = parsed["published_at"].strip()

    passages = parsed.get("verified_passages") or []
    if isinstance(passages, list):
        clean_passages: list[VerifiedPassage] = []
        for p in passages[:3]:
            if not isinstance(p, dict):
                continue
            quote = str(p.get("quote", "")).strip()
            if not quote:
                continue
            # Substring guard: drop quotes the model invented.
            if quote not in ws.cleaned_text:
                continue
            status = p.get("status", "unverified")
            if status not in ("ok", "conflict", "unverified"):
                status = "unverified"
            clean_passages.append(
                VerifiedPassage(
                    quote=quote,
                    verified_against=p.get("verified_against") or None,
                    status=status,
                )
            )
        ws.verified_passages = clean_passages

    notes = parsed.get("validity_notes") or []
    if isinstance(notes, list):
        ws.validity_notes.extend(str(n) for n in notes if n)

    return ws
