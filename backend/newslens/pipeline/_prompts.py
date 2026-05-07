"""Read prompt files from newslens/prompts/."""

from __future__ import annotations

from functools import lru_cache

from .. import config


@lru_cache(maxsize=None)
def load(name: str) -> str:
    path = config.PROMPTS_DIR / f"{name}.md"
    return path.read_text()
