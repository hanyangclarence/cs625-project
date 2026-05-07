"""Runtime configuration. Loads .env from the backend/ directory on import."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = BACKEND_ROOT.parent

load_dotenv(BACKEND_ROOT / ".env")

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
USER_AGENT = os.environ.get("USER_AGENT", "newslens-research/0.1")

# Defaults are tuned for cheapest end-to-end runs. Override with env vars to
# opt back into Opus on the heavier reasoning stages (aligner, evidence, etc.).
MODEL = os.environ.get("NEWSLENS_MODEL", "claude-haiku-4-5")
MODEL_FAST = os.environ.get("NEWSLENS_MODEL_FAST", "claude-haiku-4-5")

WORKSPACES_DIR = BACKEND_ROOT / "workspaces"
CACHE_DIR = BACKEND_ROOT / ".cache" / "llm"
FEEDBACK_DIR = BACKEND_ROOT / "feedback"
AB_RUNS_DIR = BACKEND_ROOT / "ab" / "runs"
PROMPTS_DIR = BACKEND_ROOT / "newslens" / "prompts"

PUBLIC_DATA_DIR = REPO_ROOT / "public" / "data"


def require_api_key() -> str:
    if not ANTHROPIC_API_KEY:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy backend/.env.example to backend/.env "
            "and fill it in."
        )
    return ANTHROPIC_API_KEY
