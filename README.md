# AI News Comparison — Milestone 2

A static prototype of the cross-source news comparison interface described in the Milestone 2 report. Built with **Vite + React + TypeScript + Tailwind CSS**, with a single hand-authored example (Artemis II lunar flyby) and three connected views: Cross-Source Comparison, Evidence Trace, and Claim Timeline.

## Prerequisites

- Node.js 20+ and npm

## Run locally

```bash
cd /home/hanyang/code/course/cs625
npm install   # only the first time
npm run dev
```

Then open **http://localhost:5173/** in your browser. Vite auto-reloads on file changes. Press `Ctrl+C` in the terminal to stop the server.

If you're on Windows accessing this through WSL and `localhost` doesn't load, expose the server on the network and use the WSL IP:

```bash
npm run dev -- --host
```

Use the URL Vite prints next to **Network**, or run `wsl hostname -I` from PowerShell to get the IP and visit `http://<ip>:5173/`.

## Build a static site

```bash
npm run build       # produces dist/
npm run preview     # serves dist/ at http://localhost:4173/
```

The `dist/` folder is plain static assets — deploy it to GitHub Pages, Netlify, Vercel, or any static host. No backend needed.

## Project layout

```
src/
├─ App.tsx                       phone-frame shell + active view state
├─ data/artemis.ts               hand-authored Artemis II dataset
├─ types/news.ts                 shared TypeScript interfaces
└─ components/
   ├─ PhoneFrame.tsx             outer device chrome
   ├─ SearchBar.tsx              topic search + View options trigger
   ├─ BottomTabs.tsx             three-view switcher
   ├─ MatchTag.tsx               shared/framing/evidence chip
   ├─ TrustBadge.tsx             High/Medium/Low pill
   ├─ StageTag.tsx               Appears / Picked up / Supplemented
   ├─ ViewOptionsSheet.tsx       filter drawer (sources, tags, expand-all)
   └─ views/
      ├─ CrossSourceView.tsx
      ├─ EvidenceTraceView.tsx
      └─ ClaimTimelineView.tsx
```

All "AI" outputs (trust scores, match tags, evidence support levels, timeline stages) are precomputed in `src/data/artemis.ts` — there are no runtime API calls.
