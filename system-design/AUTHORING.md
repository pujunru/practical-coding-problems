# Authoring system design questions

One JSON document per question. Validate with `python3 tools/sd.py check`;
after adding files run `python3 tools/sd.py build` to refresh the index.
`python3 tools/sd.py coverage` lists what is missing.

Write in English. Be correct above all: every answer key, number and claim must
be right, and say which convention you assume when one exists.

## Design questions: `questions/<question-id>.json`

The question must already be listed in `questions/categories.json`.

```json
{
  "id": "url-shortener",
  "title": "Design a URL Shortener",
  "prompt": "Markdown: the scenario in your own words plus one or two scale hints.",
  "clarify": ["Questions a strong candidate asks first", "..."],
  "minutes": 45,
  "reference": {
    "requirements": "...", "estimation": "...", "api": "...", "data": "...",
    "design": "...", "deepdives": "...", "wrapup": "..."
  },
  "rubric": [ {"text": "What a strong answer covers", "keywords": ["lowercase", "fragments"], "points": 1} ]
}
```

- `reference` has all seven steps, Markdown, ~400–800 words in total. Numbers
  in `estimation` must be arithmetically right. `design` may include a small
  ASCII diagram in a code block. `deepdives` covers the two or three hardest
  parts with real trade-offs.
- `rubric`: 8–12 items, the things an interviewer would check, 1–2 points each.
  `keywords` are lowercase substrings that suggest the item was mentioned
  (they only show a hint; the user ticks items themselves). Prefer specific
  terms (`"fencing"`, `"idempotency key"`) over generic ones (`"cache"` alone
  is fine only when caching *is* the item).
- Write the prompt and reference yourself. Do not copy text from other sites.

Exemplar: `questions/url-shortener.json`.
