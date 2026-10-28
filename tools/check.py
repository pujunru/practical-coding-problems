"""Validate the bank: python3 tools/check.py path/to/harness.py

- every index entry has a well-formed id and a directory with every file;
- every problem directory is listed in the index;
- each level has a statement, a title, at least one example case, and cases
  whose ops and args line up;
- the reference solution passes every case, and the starter does not.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("problem.json", "starter.py", "solution.py")
DIFFICULTIES = {"Easy", "Medium", "Hard"}


def load_harness(path):
    spec = importlib.util.spec_from_file_location("harness", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_problem(harness, pid, folder, errors):
    problem = json.loads((folder / "problem.json").read_text())
    levels = problem.get("levels") or []
    if not levels:
        errors.append(f"{pid}: problem.json has no levels")
        return
    solution = (folder / "solution.py").read_text()
    all_cases = []
    for n, level in enumerate(levels, 1):
        where = f"{pid} level {n}"
        if not level.get("title"):
            errors.append(f"{where}: missing title")
        if not (folder / "levels" / f"{n}.md").is_file():
            errors.append(f"{where}: missing levels/{n}.md")
        cases = level.get("cases") or []
        if not any(c.get("example") for c in cases):
            errors.append(f"{where}: needs at least one case marked example")
        for i, case in enumerate(cases, 1):
            if not (len(case["ops"]) == len(case["args"]) == len(case.get("expected", []))):
                errors.append(f"{where} case {i}: ops, args and expected differ in length")
        report = harness.run(solution, cases)
        failed = [i for i, c in enumerate(report["cases"], 1) if not c["passed"]]
        if report["error"] or failed:
            errors.append(f"{where}: reference solution fails cases {failed or report['error']}")
        all_cases += cases
    if harness.run((folder / "starter.py").read_text(), all_cases)["ok"]:
        errors.append(f"{pid}: the starter already passes every case")
    print(f"{pid}: {len(levels)} levels, {len(all_cases)} cases checked")


def main():
    harness = load_harness(sys.argv[1])
    errors = []
    index = json.loads((ROOT / "index.json").read_text())
    ids = [p["id"] for p in index["problems"]]

    if len(ids) != len(set(ids)):
        errors.append("index.json has duplicate ids")
    on_disk = {p.name for p in (ROOT / "problems").iterdir() if p.is_dir()}
    for missing in sorted(on_disk - set(ids)):
        errors.append(f"problems/{missing} is not listed in index.json")

    for entry in index["problems"]:
        pid = entry["id"]
        if not re.fullmatch(r"[a-z0-9-]+", pid):
            errors.append(f"{pid}: id must match [a-z0-9-]+")
            continue
        if entry.get("difficulty") not in DIFFICULTIES:
            errors.append(f"{pid}: difficulty must be one of {sorted(DIFFICULTIES)}")
        folder = ROOT / "problems" / pid
        absent = [f for f in REQUIRED if not (folder / f).is_file()]
        if absent:
            errors.append(f"{pid}: missing {', '.join(absent)}")
            continue
        check_problem(harness, pid, folder, errors)

    for e in errors:
        print(f"ERROR {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
