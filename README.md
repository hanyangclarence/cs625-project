# NewsLens

Cross-source news comparison prototype. **Vite + React + TypeScript + Tailwind** frontend with two connected views (Cross-Source Comparison and Claim Trace), backed by an agentic **Python** pipeline (`backend/`) that turns a topic string into the `Topic` JSON the UI consumes. The frontend stays fully static-deployable: it fetches `public/data/<topic-id>.json` at runtime and falls back to the hand-authored Artemis II example bundled in `src/data/artemis.ts` when no backend output is present.

## Prerequisites

- Node.js 20+ and npm

## Run the frontend

```bash
npm install   # first time
npm run dev   # http://localhost:5173/
```

If you're on Windows accessing through WSL, use `npm run dev -- --host` and visit the WSL IP Vite prints under **Network**.

## Build a static site

```bash
npm run build       # produces dist/
npm run preview     # serves dist/ at http://localhost:4173/
```

The `dist/` folder is plain static assets — deploy it to GitHub Pages, Netlify, Vercel, or any static host. The site works with or without the backend's generated `public/data/<id>.json`; without it, the bundled Artemis II example is shown.

## Run the backend

The backend lives in `backend/` and turns a topic string into the `Topic` JSON the frontend consumes. It uses Anthropic's API (model + built-in `web_search` tool).

```bash
conda activate cs625
cd backend
pip install -e .
cp .env.example .env       # fill in ANTHROPIC_API_KEY

python -m newslens.cli run \
  --topic "Artemis II lunar flyby" \
  --topic-id artemis-ii-lunar-flyby
```

Output JSON lands at `../public/data/<topic-id>.json` and is picked up by the frontend automatically. See `backend/README.md` for `--resume`, expert audit, A/B harness, and the feedback API.

## Project layout

```
src/                              frontend
├─ App.tsx                        shell + topic fetch + fallback
├─ data/artemis.ts                hand-authored offline fallback
├─ types/news.ts                  shared TypeScript types
└─ components/
   ├─ PhoneFrame.tsx              device chrome
   ├─ SearchBar.tsx, BottomTabs.tsx, ViewOptionsSheet.tsx
   ├─ MatchTag.tsx, TrustBadge.tsx, StageTag.tsx
   └─ views/
      ├─ CrossSourceView.tsx
      └─ ClaimTraceView.tsx       merged evidence + timeline per claim

backend/                          Python pipeline
└─ newslens/
   ├─ cli.py, run.py              orchestrator + CLI entrypoints
   ├─ llm.py, cache.py            Anthropic wrapper + content-hash cache
   ├─ sources/                    feeds, crawler, extract
   ├─ pipeline/                   cleaner, inspector, verifier (ReAct), claims, trust, aligner, lenses, evidence, timeline, exporter
   ├─ workspaces/                 pydantic schemas + JSON store
   ├─ prompts/*.md                one prompt per stage
   ├─ feedback/                   FastAPI signals + audit + report
   └─ ab/                         prompt-variant harness

public/data/<topic-id>.json        contract surface between backend → frontend
```
