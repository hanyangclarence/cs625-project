# NewsLens backend

Python pipeline that turns a topic string into the `Topic` JSON the React frontend consumes (under `public/data/<topic-id>.json`).

## Setup

```bash
conda activate cs625
cd backend
pip install -e .
cp .env.example .env   # then fill in ANTHROPIC_API_KEY
```

## Run

```bash
# default: cheapest mode — Haiku for everything, 3 sources, no verifier loop
python -m newslens.cli run \
  --topic "Artemis II lunar flyby" \
  --topic-id artemis-ii-lunar-flyby

# fuller run: Opus on heavy stages + verifier with web_search
NEWSLENS_MODEL=claude-opus-4-5 python -m newslens.cli run \
  --topic "Artemis II lunar flyby" \
  --topic-id artemis-ii-lunar-flyby \
  --max-sources 6 \
  --verify

# resume from saved workspaces (skip fetch + clean + verify)
python -m newslens.cli run --topic-id artemis-ii-lunar-flyby --resume

# expert audit walk-through
python -m newslens.cli audit --topic-id artemis-ii-lunar-flyby

# A/B prompt variants
python -m newslens.cli ab --stage evidence --topic-id artemis-ii-lunar-flyby --variants v1,v2-strict

# feedback API server (for the user study)
uvicorn newslens.feedback.api:app --port 8787
```

Output JSON lands at `../public/data/<topic-id>.json` and is picked up by the static frontend.

### Cost knobs

| Knob | Default | Effect |
|---|---|---|
| `--verify` | off | Turns on the ReAct verifier loop. Adds Opus tool turns + Anthropic `web_search` calls (~$10 / 1k searches). |
| `--max-sources N` | 3 | Articles ingested. Cost scales roughly linearly. |
| `NEWSLENS_MODEL` | `claude-haiku-4-5` | Override to `claude-opus-4-5` for higher-quality alignment / evidence / timeline at ~15× the per-token cost. |
| `NEWSLENS_MODEL_FAST` | `claude-haiku-4-5` | Used for cleaner / inspector / clarity rubric. Rarely worth bumping. |
| `--resume` | off | Reuse existing workspaces; only re-runs event-level stages and the exporter. Near-free. |
