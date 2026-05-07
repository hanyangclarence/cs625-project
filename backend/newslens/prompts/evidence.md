For one canonical claim and one news article, find the single best supporting passage in the article.

Output a JSON object:

```
{
  "passage": "verbatim span from the article body, or empty string if no good support",
  "supportLevel": "strong" | "partial" | "weaker",
  "score": int 0..100,
  "rationale": "one short sentence"
}
```

Rules:
- `passage` MUST be a verbatim substring of the article body. No paraphrase, no ellipses, no quotes added.
- `strong`: passage directly states the claim with the same key figures/entities.
- `partial`: passage acknowledges the claim but with hedging, missing detail, or attribution to another party.
- `weaker`: passage is tangentially related, framed differently, or only weakly implies the claim.
- If the article does not support the claim at all, return `{"passage": "", "supportLevel": "weaker", "score": 0, "rationale": "..."}`. The downstream pipeline will drop empty passages.
- Output JSON only.
