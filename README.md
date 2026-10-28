# Practical Coding — problems

The problem bank for [Practical Coding](https://github.com/pujunru/practical-coding):
"implement this component" interview problems in Python, each with a test suite
you run in the browser at https://pujunru.github.io/practical-coding/.

## System design

`system-design/` holds the two system design modules:

- `fundamentals/` — one JSON file per concept: a short mental model and 4–6
  drills (multiple choice, ordering, estimates, recall).
  `categories.json` is the full concept map; `index.json` is generated.
- `questions/` — one JSON file per design question: prompt, clarifying
  questions, a reference outline for each interview step, and a self-check
  rubric. `categories.json` is the full question list; `index.json` is
  generated.

See [system-design/AUTHORING.md](system-design/AUTHORING.md) for the format,
and run `python3 tools/sd.py check` before committing.

## Layout

```
index.json                       the problem list: id, title, difficulty, tags
problems/<id>/problem.json       levels, each with a title and its test cases
problems/<id>/levels/<n>.md      statement of level n (Markdown)
problems/<id>/starter.py         what the editor starts with
problems/<id>/solution.py        reference solution; checked by CI, and used to
                                 compute expected output for custom testcases
tools/check.py                   validates the bank against the app's harness
```

## Writing a problem

- Split the problem into levels that build on each other. Level `n`'s
  statement lives in `levels/<n>.md`; its title and cases live in
  `problem.json`.
- A case is LeetCode's design-problem format:

  ```json
  {"ops":      ["RateLimiter", "allow",  "allow"],
   "args":     [[2, 10],       ["a", 0], ["a", 5]],
   "expected": [null,          true,     true],
   "example": true}
  ```

  The first op constructs the class; each later op calls a method on it.
  `{"raises": "ValueError"}` means the call must raise. Floats match within
  1e-6.
- Mark at least one case per level `"example": true`. Examples appear in the
  statement and seed the Testcase tab; `"explanation"` is shown under them.
- Keep cases deterministic: pass time in as an argument rather than reading a
  clock.
- Ids match `[a-z0-9-]+`. Difficulty is `Easy`, `Medium` or `Hard`.

## Check

```sh
git clone https://github.com/pujunru/practical-coding.git ../practical-coding
python3 tools/check.py ../practical-coding/runner/harness.py
```

CI runs the same check: every level is well formed, every reference solution
passes every case, no starter passes, and `index.json` matches the `problems/`
folders.

## License

MIT.
