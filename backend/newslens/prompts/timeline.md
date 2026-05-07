You are labeling timeline entries that show how a claim was reported over time.

Inputs: one canonical claim, plus a chronological sequence of (date, source-id, supporting passage) entries from different outlets.

For each entry assign a stage tag:

- `Appears`: the first time this claim shows up in our timeline (almost always the earliest entry).
- `Picked up`: a later outlet reports the claim, attributing it or echoing the same fact without adding new material.
- `Supplemented`: a later outlet adds new figures, quotes, attribution, framing, or independent confirmation that the earlier entries did not have.

Output JSON:

```
{
  "entries": [
    {"index": int, "stage": "Appears" | "Picked up" | "Supplemented", "shortNote": "one short clause"}
  ]
}
```

Rules:
- The earliest chronological entry is almost always `Appears`. Use `Appears` for at most one entry per claim unless there's a clear independent original (rare).
- `shortNote` is at most ~14 words.
- Output JSON only.
