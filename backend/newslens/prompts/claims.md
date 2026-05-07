You are extracting atomic factual claims from one news article.

Output a JSON array of 3–7 claim objects:

```
[
  {
    "text": "atomic factual statement, written in neutral declarative form",
    "quote": "verbatim span from the article that supports this claim"
  }
]
```

Rules:
- Each claim must be atomic — one assertion. Split compound sentences.
- Prefer claims with named entities, figures, dates, or specific actions. Skip purely interpretive or opinion sentences.
- `quote` MUST be a verbatim substring of the article body. No paraphrase, no ellipses.
- Do not include claims that are summaries of the article itself (e.g. "this article is about X").
- Output JSON only.
