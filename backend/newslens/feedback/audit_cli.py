"""Walk an expert through audit prompts for one topic.

Loads the EventWorkspace + ArticleWorkspaces from disk, walks the expert
through (a) per-source validity, (b) per-canonical-claim alignment, (c)
per-evidence support correctness, (d) per-timeline ordering. Writes labels
into feedback/audit/<topic-id>.jsonl.
"""

from __future__ import annotations

from ..workspaces import store as ws_store
from . import store as fb_store


def _ask(prompt: str) -> str:
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return "q"


def _label_or_skip(prompt: str) -> str | None:
    while True:
        ans = _ask(prompt + " [y=correct / n=incorrect / s=skip / q=quit] ")
        if ans in ("y", "n"):
            return "correct" if ans == "y" else "incorrect"
        if ans == "s":
            return None
        if ans == "q":
            raise SystemExit(0)


def walk(topic_id: str) -> None:
    event = ws_store.load_event(topic_id)
    if not event:
        print(f"No event workspace found for topic_id={topic_id}")
        return
    articles = {a.id: a for a in ws_store.list_articles(topic_id)}
    print(f"Audit: {event.title} ({topic_id})")
    print("=" * 60)

    print("\n[1/4] Source validity")
    for sid, lens in event.lenses.items():
        ws = articles.get(sid)
        if not ws:
            continue
        print(f"\n  source={sid} outlet={ws.outlet} matchTag={lens.matchTag}")
        if ws.validity_notes:
            for n in ws.validity_notes:
                print(f"    note: {n}")
        label = _label_or_skip("  Verdict?")
        if label:
            fb_store.append_audit(
                topic_id, {"target": "source", "target_id": sid, "label": label}
            )

    print("\n[2/4] Claim alignment")
    for c in event.canonical_claims:
        print(f"\n  claim={c.id}")
        print(f"    text: {c.text}")
        print(f"    refs: {', '.join(c.article_claim_refs)}")
        label = _label_or_skip("  Alignment correct?")
        if label:
            fb_store.append_audit(
                topic_id, {"target": "claim", "target_id": c.id, "label": label}
            )

    print("\n[3/4] Evidence support")
    for claim_id, items in event.evidence_index.items():
        for it in items:
            print(f"\n  claim={claim_id} source={it.sourceId} level={it.supportLevel} score={it.score}")
            print(f"    passage: {it.passage[:240]}{'…' if len(it.passage) > 240 else ''}")
            label = _label_or_skip("  Support level correct?")
            if label:
                fb_store.append_audit(
                    topic_id,
                    {
                        "target": "evidence",
                        "target_id": f"{claim_id}|{it.sourceId}",
                        "label": label,
                    },
                )

    print("\n[4/4] Timeline ordering")
    for i, t in enumerate(event.timeline_index):
        print(f"\n  entry {i+1}: date={t.date} source={t.sourceId} stage={t.stage}")
        if t.shortNote:
            print(f"    note: {t.shortNote}")
        label = _label_or_skip("  Stage correct?")
        if label:
            fb_store.append_audit(
                topic_id,
                {
                    "target": "timeline",
                    "target_id": f"{t.claimId or '_'}#{i}",
                    "label": label,
                },
            )

    print("\nAudit complete. Labels appended to feedback/audit/" + topic_id + ".jsonl")
