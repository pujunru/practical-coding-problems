# Authoring system design content

Two kinds of files, each one JSON document. Validate with
`python3 tools/sd.py check`; after adding files run `python3 tools/sd.py build`
to refresh the indexes. `python3 tools/sd.py coverage` lists what is missing.

Write in English. Be correct above all: every answer key, number and claim must
be right, and say which convention you assume when one exists.

## Fundamentals: `fundamentals/<concept-id>.json`

A concept is a **guide**, not a quiz: there are no auto-graded answers. It
teaches how to explain the concept, the model to draw or name, and the details
an interviewer will probe, then gives prompts to answer out loud. The concept
must already be listed in `fundamentals/categories.json`.

```json
{
  "id": "fencing-token",
  "title": "Fencing Token",
  "explain": "Markdown, 2–4 sentences: what you would say in the first 30 seconds.",
  "model": "Markdown: the model to draw or name — steps, components, a small ASCII diagram, named variants. 80–200 words.",
  "details": [
    {"q": "A probe an interviewer asks", "a": "Markdown answer, 1–4 sentences, with the why."}
  ],
  "prompts": [
    {"q": "Something to explain out loud", "points": ["A key point a good answer covers", "..."]}
  ]
}
```

- `explain`: plain, spoken English — the version you would actually say. Lead
  with what problem it solves.
- `model`: the mechanism or the mental model and its usual variants. Use the
  user's own analogies and framings from their note.
- `details`: 4–8 probes, ordered from basic to sharp. These are the follow-up
  questions ("why not X?", "what breaks when…?", "how do you size…?") with
  short answers. Numbers belong here as rules of thumb, not as quiz answers.
- `prompts`: 2–4 out-loud prompts ("Explain…", "Walk through…", "Compare…
  and say when you would pick each"), each with 3–7 key points the user ticks
  off after answering. Points are short and concrete.

Exemplars: `fundamentals/high-level-thinking.json`, `fundamentals/lease.json`,
`fundamentals/fencing-token.json`, `fundamentals/consistent-hashing.json`.

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
  "rubric": [ {"text": "What a strong answer covers", "keywords": ["lowercase", "fragments"], "points": 1} ],
  "concepts": ["fundamentals concept ids this question exercises"]
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
- `concepts`: 3–8 ids from `fundamentals/categories.json`.
- Write the prompt and reference yourself. Do not copy text from other sites.

Exemplar: `questions/url-shortener.json`.
