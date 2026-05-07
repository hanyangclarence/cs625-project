"""Anthropic client wrapper with prompt caching + content-hash disk cache.

Two main entry points:
  - call_text(...): plain text completion, returns the assistant's text.
  - call_json(...): asks for JSON, parses it, returns a dict/list.

Both accept optional `cached_blocks`: a list of strings that should be marked
with cache_control: ephemeral (the content reused across many calls — article
text, canonical claim list, tool definitions). Place the long stable content
first; the per-call instruction goes last and is NOT cached.
"""

from __future__ import annotations

import json
import re
import time
from typing import Any, Iterable

from anthropic import Anthropic

from . import cache, config

_client: Anthropic | None = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(api_key=config.require_api_key())
    return _client


def _build_system(blocks: Iterable[str], cache_last: bool = True) -> list[dict[str, Any]]:
    """Build a system parameter as a list of content blocks. The final block
    gets cache_control if cache_last is True."""
    items = [{"type": "text", "text": b} for b in blocks if b]
    if items and cache_last:
        items[-1] = {**items[-1], "cache_control": {"type": "ephemeral"}}
    return items


def _strip_code_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        s = re.sub(r"^```[a-zA-Z0-9]*\n", "", s)
        s = re.sub(r"\n```$", "", s)
    return s.strip()


def call_text(
    *,
    instruction: str,
    cached_blocks: list[str] | None = None,
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.2,
    use_disk_cache: bool = True,
) -> str:
    model = model or config.MODEL
    system = _build_system(cached_blocks or [])
    payload = {
        "model": model,
        "system": system,
        "instruction": instruction,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    cache_key = cache.make_key(payload)
    if use_disk_cache:
        hit = cache.get(cache_key)
        if hit is not None:
            return hit["text"]

    msg = client().messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system,
        messages=[{"role": "user", "content": instruction}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", None) == "text")
    if use_disk_cache:
        cache.put(cache_key, {"text": text, "model": model, "ts": time.time()})
    return text


def call_json(
    *,
    instruction: str,
    cached_blocks: list[str] | None = None,
    model: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.1,
    use_disk_cache: bool = True,
) -> Any:
    """Like call_text but parses a JSON object/array out of the reply.

    Tolerates ```json fences and stray prose around the JSON block.
    """
    raw = call_text(
        instruction=instruction
        + "\n\nReturn ONLY a valid JSON value (object or array). "
        "No prose, no markdown fences.",
        cached_blocks=cached_blocks,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        use_disk_cache=use_disk_cache,
    )
    cleaned = _strip_code_fence(raw)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Recover the largest {…} or […] block.
        match = re.search(r"(\{.*\}|\[.*\])", cleaned, flags=re.DOTALL)
        if not match:
            raise ValueError(f"Model did not return parseable JSON: {raw[:400]!r}")
        return json.loads(match.group(1))


def call_with_tools(
    *,
    instruction: str,
    tools: list[dict[str, Any]],
    tool_runner,
    cached_blocks: list[str] | None = None,
    model: str | None = None,
    max_tool_calls: int = 6,
    max_tokens: int = 4096,
    temperature: float = 0.2,
) -> tuple[str, list[dict[str, Any]]]:
    """Run a hand-rolled ReAct-ish loop.

    `tools` is the Anthropic tool spec list (must include any server tools like
    `{"type": "web_search_20251119", "name": "web_search"}` and any custom
    tools).

    `tool_runner(name, input) -> str` is called for any *custom* tool the model
    invokes. Server-side tools (e.g. web_search) are executed by Anthropic and
    don't reach the runner.

    Returns (final_assistant_text, eval_log). eval_log is a list of step dicts
    suitable for storing in ArticleWorkspace.eval_log.
    """
    model = model or config.MODEL
    system = _build_system(cached_blocks or [])
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": instruction},
    ]
    log: list[dict[str, Any]] = []
    tool_calls = 0

    while True:
        resp = client().messages.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system,
            tools=tools,
            messages=messages,
        )
        # Append assistant turn verbatim so subsequent tool_result blocks resolve.
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            text = "".join(
                b.text for b in resp.content if getattr(b, "type", None) == "text"
            )
            return text, log

        # Run any custom tool_use blocks; record server tool_use blocks for the log.
        tool_results: list[dict[str, Any]] = []
        for block in resp.content:
            btype = getattr(block, "type", None)
            if btype != "tool_use":
                continue
            tool_calls += 1
            log.append(
                {
                    "step": "tool_use",
                    "tool": block.name,
                    "input": getattr(block, "input", {}),
                }
            )
            # Server-managed tools (like web_search) come back already executed
            # in the assistant turn as tool_result blocks Anthropic injects;
            # we don't need to run them. We only run client-side tools.
            try:
                result = tool_runner(block.name, getattr(block, "input", {}))
            except Exception as exc:  # noqa: BLE001
                result = f"ERROR: {exc!s}"
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                }
            )
        if tool_results:
            messages.append({"role": "user", "content": tool_results})

        if tool_calls >= max_tool_calls:
            log.append({"step": "tool_cap_reached", "cap": max_tool_calls})
            # Force a final answer by sending a nudge.
            messages.append(
                {
                    "role": "user",
                    "content": "Tool budget exhausted. Provide your final answer now.",
                }
            )
            final = client().messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system,
                messages=messages,
            )
            text = "".join(
                b.text for b in final.content if getattr(b, "type", None) == "text"
            )
            return text, log
