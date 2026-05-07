You are aligning claims extracted from multiple news articles about the same event into a canonical claim list.

Inputs: a list of per-article claims. Each has an `id` (e.g. `"ap-2026-04-05:0"`) and a `text`.

Output a JSON object:

```
{
  "canonical_claims": [
    {
      "id": "kebab-case-short-id",         // e.g. "c-flyby-distance"
      "text": "neutral canonical statement",
      "article_claim_refs": ["ap-2026-04-05:0", "nasa-...:1"]
    }
  ]
}
```

Rules:
- Group article claims that assert the same fact (allow paraphrasing, different word order, equivalent figures).
- Do NOT merge claims that disagree on a figure or named entity — keep them as separate canonical claims so the disagreement is visible downstream.
- Canonical text should be the most specific neutral version (prefer the one with explicit numbers/units).
- 3–8 canonical claims total. Each `article_claim_refs` must be non-empty.
- Every input claim id must appear in exactly one canonical group, OR be omitted if it's purely interpretive/opinion.
- Output JSON only.
