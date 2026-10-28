# Authoring system design content

Two kinds of files, each one JSON document. Validate with
`python3 tools/sd.py check`; after adding files run `python3 tools/sd.py build`
to refresh the indexes. `python3 tools/sd.py coverage` lists what is missing.

Write in English. Be correct above all: every answer key, number and claim must
be right, and say which convention you assume when one exists.

## Fundamentals: `fundamentals/<concept-id>.json`

The concept must already be listed in `fundamentals/categories.json` (that list
is the plan; do not invent ids).

```json
{
  "id": "consistent-hashing",
  "title": "Consistent Hashing",
  "summary": "Markdown, 120–250 words: the mental model first, then when to use it and when not to.",
  "drills": [ ... 4 to 6 drills ... ]
}
```

Drill types (use at least three different types per concept; Markdown is
allowed in every text field):

| type | fields | notes |
| --- | --- | --- |
| `choice` | `q`, `options` (3–5), `answer` (list of correct option indexes), `explain` | More than one index = "select all that apply". Options are shuffled on screen, so never write "all of the above". Wrong options must be plausible misconceptions, not jokes. |
| `order` | `q`, `items` (3–6, **in the correct order**), `explain` | Use for processes, state machines, request paths. |
| `number` | `q`, `answer`, `unit`, `tolerance` (fraction, 0 = exact), `explain` | Back-of-the-envelope or exact quantities. Give every assumption in `q`. Use 0.3–0.5 tolerance for estimates. |
| `recall` | `q`, `answer` (reference, Markdown) | Self-graded. One per concept is plenty. |

A good drill tests a decision or a mechanism ("what breaks if…", "which
component owns…", "what happens next"), not a definition someone could
pattern-match. Scenario stems beat "Which of the following is true".
`explain` says *why* in one to three sentences, including why the tempting
wrong answer is wrong.

Exemplars: `fundamentals/lease.json`, `fundamentals/fencing-token.json`,
`fundamentals/consistent-hashing.json`.

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
