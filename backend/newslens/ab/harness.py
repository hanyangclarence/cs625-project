"""A/B prompt-variant runner.

Variants live as YAML files at:
  backend/newslens/ab/variants/<stage>/<variant_id>.yml

Each YAML has:
  prompt_override: |
    Replacement system prompt for this stage.
  notes: free text

Currently supported stages:
  - evidence: re-runs evidence.map_evidence with the override prompt.
  - lenses:   re-runs lenses.assign with the override prompt.
  - aligner:  re-runs aligner.align with the override prompt.

Outputs land at:
  backend/ab/runs/<run-id>/<variant_id>.json

Plus an aggregated diff at runs/<run-id>/summary.md.
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path

import yaml

from .. import config
from ..pipeline import _prompts, aligner, evidence as evidence_stage, lenses
from ..workspaces import store as ws_store


@contextmanager
def _override_prompt(name: str, body: str):
    original = _prompts.load.cache_info()
    # Patch by writing to the cache directly.
    _prompts.load.cache_clear()
    real = _prompts.load
    def patched(n: str) -> str:
        return body if n == name else real.__wrapped__(n)
    _prompts.load = patched  # type: ignore[assignment]
    try:
        yield
    finally:
        _prompts.load = real  # type: ignore[assignment]
        _ = original


def _load_variant(stage: str, variant_id: str) -> dict:
    path = config.BACKEND_ROOT / "newslens" / "ab" / "variants" / stage / f"{variant_id}.yml"
    if not path.exists():
        raise FileNotFoundError(f"variant not found: {path}")
    return yaml.safe_load(path.read_text())


def _run_one_variant(*, topic_id: str, stage: str, variant_id: str) -> dict:
    variant = _load_variant(stage, variant_id)
    body = variant.get("prompt_override", "").strip()
    if not body:
        raise ValueError(f"variant {variant_id} missing prompt_override")

    articles = ws_store.list_articles(topic_id)
    articles = [a for a in articles if a.cleaned_text]
    event = ws_store.load_event(topic_id)
    if not event:
        raise RuntimeError(f"no EventWorkspace; run pipeline first for {topic_id}")

    with _override_prompt(stage, body):
        if stage == "evidence":
            out = evidence_stage.map_evidence(articles, event.canonical_claims)
            return {"evidence_index": {k: [v.model_dump() for v in vs] for k, vs in out.items()}}
        if stage == "lenses":
            out = lenses.assign(articles, event.canonical_claims)
            return {"lenses": {k: v.model_dump() for k, v in out.items()}}
        if stage == "aligner":
            out = aligner.align(articles)
            return {"canonical_claims": [c.model_dump() for c in out]}
    raise ValueError(f"stage {stage} not supported in A/B harness yet")


def run(*, topic_id: str, stage: str, variant_ids: list[str]) -> Path:
    run_id = f"{stage}-{int(time.time())}"
    out_dir = config.AB_RUNS_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    summaries: dict[str, dict] = {}
    for vid in variant_ids:
        print(f"[ab] {stage} variant={vid}")
        result = _run_one_variant(topic_id=topic_id, stage=stage, variant_id=vid)
        path = out_dir / f"{vid}.json"
        path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        summaries[vid] = result

    summary_md = ["# A/B run", f"- topic: {topic_id}", f"- stage: {stage}", ""]
    for vid in variant_ids:
        result = summaries[vid]
        summary_md.append(f"## {vid}")
        if stage == "evidence":
            for cid, items in (result.get("evidence_index") or {}).items():
                if not items:
                    summary_md.append(f"- {cid}: 0 items")
                    continue
                avg = sum(it["score"] for it in items) / len(items)
                summary_md.append(f"- {cid}: {len(items)} items, avg score {avg:.1f}")
        elif stage == "lenses":
            for sid, lt in (result.get("lenses") or {}).items():
                summary_md.append(f"- {sid}: {lt['matchTag']} ({lt['matchScore']})")
        elif stage == "aligner":
            for c in result.get("canonical_claims", []):
                summary_md.append(f"- {c['id']}: {len(c.get('article_claim_refs', []))} refs")
        summary_md.append("")
    (out_dir / "summary.md").write_text("\n".join(summary_md))
    print(f"[ab] wrote {out_dir}")
    return out_dir
