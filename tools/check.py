"""Validate the bank: python3 tools/check.py path/to/harness.py

- every index entry has a well-formed id and a directory with all four files;
- every problem directory is listed in the index;
- the reference solution passes every test, and the starter does not.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = ("README.md", "starter.py", "tests.py", "solution.py")
DIFFICULTIES = {"Easy", "Medium", "Hard"}


def load_harness(path):
    spec = importlib.util.spec_from_file_location("harness", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
        tests = (folder / "tests.py").read_text()

        report = harness.run((folder / "solution.py").read_text(), tests)
        if not report["tests"]:
            errors.append(f"{pid}: tests.py defines no test_* functions")
        elif not report["ok"]:
            failed = [t["name"] for t in report["tests"] if not t["passed"]] or [report["error"]]
            errors.append(f"{pid}: reference solution fails {failed}")

        if harness.run((folder / "starter.py").read_text(), tests)["ok"]:
            errors.append(f"{pid}: the starter already passes every test")

        print(f"{pid}: {len(report['tests'])} tests checked")

    for e in errors:
        print(f"ERROR {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
