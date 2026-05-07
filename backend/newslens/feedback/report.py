"""Aggregate signals + audit into a Markdown summary.

Run:
  python -m newslens.feedback.report --topic-id artemis-ii-lunar-flyby
"""

from __future__ import annotations

import argparse
from collections import Counter

from . import store


def summarize(topic_id: str) -> str:
    signals = store.read("signals", topic_id)
    audit = store.read("audit", topic_id)

    lines: list[str] = [f"# Feedback report — {topic_id}", ""]

    lines.append(f"## User signals ({len(signals)})")
    by_view = Counter(s.get("view", "unknown") for s in signals)
    by_signal = Counter(s.get("signal", "?") for s in signals)
    for view, n in by_view.most_common():
        lines.append(f"- view {view}: {n}")
    lines.append(
        f"- positive: {by_signal.get('+', 0)}  /  negative: {by_signal.get('-', 0)}"
    )
    notes = [s["note"] for s in signals if s.get("note")]
    if notes:
        lines.append("")
        lines.append("### Notes")
        for n in notes[:25]:
            lines.append(f"- {n}")

    lines.append("")
    lines.append(f"## Expert audit ({len(audit)})")
    by_target = Counter(a.get("target", "?") for a in audit)
    for target in ("source", "claim", "evidence", "timeline"):
        records = [a for a in audit if a.get("target") == target]
        if not records:
            continue
        correct = sum(1 for r in records if r.get("label") == "correct")
        total = len(records)
        agreement = (correct / total * 100) if total else 0.0
        lines.append(
            f"- **{target}** agreement: {correct}/{total} = {agreement:.1f}%"
        )
    lines.append("")
    lines.append("### Counts by target")
    for target, n in by_target.most_common():
        lines.append(f"- {target}: {n}")

    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--topic-id", required=True)
    args = p.parse_args()
    print(summarize(args.topic_id))


if __name__ == "__main__":
    main()
