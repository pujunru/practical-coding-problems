"""System design question bank: build the index and validate every question.

    python3 tools/sd.py build    # rewrite questions/index.json
    python3 tools/sd.py check    # validate; exit 1 on errors
    python3 tools/sd.py coverage # list questions not written yet

questions/categories.json is the plan: every question that should exist.
questions/index.json lists only the ones that have been written, and is what
the app reads.
"""

import json
import re
import sys
from pathlib import Path

Q = Path(__file__).resolve().parent.parent / "system-design" / "questions"
STEPS = {"requirements", "estimation", "api", "data", "design", "deepdives", "wrapup"}
DIFFICULTIES = {"Easy", "Medium", "Hard"}
ID = re.compile(r"[a-z0-9-]+")


def load(path):
    return json.loads(path.read_text())


def written(item_id):
    return (Q / f"{item_id}.json").is_file()


def build():
    index = []
    for cat in load(Q / "categories.json")["categories"]:
        qs = [q for q in cat["questions"] if written(q["id"])]
        if qs:
            index.append({"title": cat["title"], "questions": qs})
    (Q / "index.json").write_text(json.dumps({"categories": index}, indent=1) + "\n")
    print(f"index: {sum(len(c['questions']) for c in index)} questions")


def check():
    errors = []
    planned = {q["id"]: q for cat in load(Q / "categories.json")["categories"] for q in cat["questions"]}
    for q in planned.values():
        if q["difficulty"] not in DIFFICULTIES or not ID.fullmatch(q["id"]):
            errors.append(f"categories.json: bad entry {q['id']}")
    for path in sorted(Q.glob("*.json")):
        if path.name in ("categories.json", "index.json"):
            continue
        qid = path.stem
        if qid not in planned:
            errors.append(f"{path.name}: not in categories.json")
            continue
        q = load(path)
        if q.get("id") != qid:
            errors.append(f"{qid}: id field must match the file name")
        if q.get("title") != planned[qid]["title"]:
            errors.append(f"{qid}: title must match categories.json")
        if not q.get("prompt"):
            errors.append(f"{qid}: missing prompt")
        ref = q.get("reference") or {}
        if set(ref) - STEPS:
            errors.append(f"{qid}: unknown reference steps {sorted(set(ref) - STEPS)}")
        if STEPS - set(ref):
            errors.append(f"{qid}: reference missing steps {sorted(STEPS - set(ref))}")
        rubric = q.get("rubric") or []
        if len(rubric) < 6:
            errors.append(f"{qid}: rubric needs at least 6 items")
        for i, r in enumerate(rubric, 1):
            if not r.get("text") or not r.get("keywords"):
                errors.append(f"{qid} rubric {i}: needs text and keywords")
        if "#/sd/f/" in json.dumps(q):
            errors.append(f"{qid}: links to the removed fundamentals module")
    before = (Q / "index.json").read_text() if (Q / "index.json").exists() else ""
    build()
    if before != (Q / "index.json").read_text():
        errors.append("index.json was stale; run `python3 tools/sd.py build` and commit the result")
    for e in errors:
        print(f"ERROR {e}")
    return errors


def coverage():
    todo = [q["id"] for cat in load(Q / "categories.json")["categories"] for q in cat["questions"] if not written(q["id"])]
    total = sum(len(cat["questions"]) for cat in load(Q / "categories.json")["categories"])
    print(f"questions: {total - len(todo)} / {total} written")
    for t in todo:
        print("  todo", t)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "build":
        build()
    elif cmd == "coverage":
        coverage()
    else:
        sys.exit(1 if check() else 0)
