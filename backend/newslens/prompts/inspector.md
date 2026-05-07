You are extracting metadata from a news article. Output a single JSON object with this shape:

```
{
  "author": string | null,           // person who reported the story; null if only an outlet byline
  "published_at": string | null,     // ISO 8601 if you can resolve a precise date; otherwise null
  "summary": string,                 // 1–2 sentence neutral summary of the article
  "references": [                    // outside sources the article cites (NOT internal links)
    {"text": "string description", "url": null | "..." }
  ]
}
```

Rules:
- Do not invent metadata. If the article does not state an author, return null.
- For `published_at`, prefer an explicit date in the byline/dateline; otherwise null. The pipeline's `dateparser` will handle alternative phrasings later.
- `references` should list things like "NASA mission briefing", "court filing in Northern District", named studies or reports, and any URLs the body cites. Cap at 8 entries.
- The summary must be neutral — no editorializing.
