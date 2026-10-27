# Practical Coding — problems

The problem bank for [Practical Coding](https://github.com/pujunru/practical-coding):
"implement this component" interview problems in Python, each with a test suite
you run in the browser at https://pujunru.github.io/practical-coding/.

## Layout

```
index.json                    the problem list: id, title, difficulty, tags
problems/<id>/README.md       the statement (Markdown)
problems/<id>/starter.py      what the editor starts with; the module is `solution`
problems/<id>/tests.py        test_* functions using plain assert
problems/<id>/solution.py     reference solution, checked by CI
tools/check.py                validates the bank against the app's harness
```

## Writing a problem

- `tests.py` imports from `solution` and defines `test_*` functions. They run in
  definition order.
- Name a test `test_l<N>_...` to put it in level N, and define
  `LEVELS = {1: "Single client", ...}` to name the levels. A test's docstring is
  its display title.
- Keep tests deterministic: pass time in as an argument rather than reading a
  clock, and avoid randomness without a fixed seed.
- Ids match `[a-z0-9-]+`. Difficulty is `Easy`, `Medium` or `Hard`.

## Check

```sh
git clone https://github.com/pujunru/practical-coding.git ../practical-coding
python3 tools/check.py ../practical-coding/runner/harness.py
```

CI runs the same check: every reference solution passes, no starter passes,
and `index.json` matches the `problems/` folders.

## License

MIT.
