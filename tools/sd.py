"""System design bank: build the indexes and validate every file.

    python3 tools/sd.py build    # rewrite fundamentals/index.json and questions/index.json
    python3 tools/sd.py check    # validate; exit 1 on errors
    python3 tools/sd.py coverage # list concepts and questions not written yet

categories.json in each folder is the plan: every concept and question that
should exist. index.json lists only the ones that have been written, and is
what the app reads.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "system-design"
F, Q = ROOT / "fundamentals", ROOT / "questions"
DRILL_TYPES = {"choice", "order", "number", "recall"}
STEPS = {"requirements", "estimation", "api", "data", "design", "deepdives", "wrapup"}
DIFFICULTIES = {"Easy", "Medium", "Hard"}
ID = re.compile(r"[a-z0-9-]+")


def load(path):
    return json.loads(path.read_text())


def written(folder, item_id):
    return (folder / f"{item_id}.json").is_file()


def build():
    cats = load(F / "categories.json")["categories"]
    index = []
    for cat in cats:
        concepts = [{"id": c["id"], "title": c["title"], "drills": len(load(F / f"{c['id']}.json")["drills"])}
                    for c in cat["concepts"] if written(F, c["id"])]
        if concepts:
            index.append({"id": cat["id"], "title": cat["title"], "concepts": concepts})
    (F / "index.json").write_text(json.dumps({"categories": index}, indent=1) + "\n")

    qcats = load(Q / "categories.json")["categories"]
    qindex = []
    for cat in qcats:
        qs = [q for q in cat["questions"] if written(Q, q["id"])]
        if qs:
            qindex.append({"title": cat["title"], "questions": qs})
    (Q / "index.json").write_text(json.dumps({"categories": qindex}, indent=1) + "\n")
    n_c = sum(len(c["concepts"]) for c in index)
    n_q = sum(len(c["questions"]) for c in qindex)
    print(f"index: {n_c} concepts, {n_q} questions")


def check_drill(where, d, errors):
    t = d.get("type")
    if t not in DRILL_TYPES:
        errors.append(f"{where}: unknown type {t!r}")
        return
    if not isinstance(d.get("q"), str) or not d["q"].strip():
        errors.append(f"{where}: missing q")
    if t == "choice":
        opts, ans = d.get("options"), d.get("answer")
        if not isinstance(opts, list) or len(opts) < 2:
            errors.append(f"{where}: choice needs at least 2 options")
        elif not isinstance(ans, list) or not ans or any(not isinstance(a, int) or not 0 <= a < len(opts) for a in ans):
            errors.append(f"{where}: answer must be a non-empty list of option indexes")
        elif len(set(map(str, opts))) != len(opts):
            errors.append(f"{where}: duplicate options")
    elif t == "order":
        if not isinstance(d.get("items"), list) or len(d["items"]) < 3:
            errors.append(f"{where}: order needs at least 3 items (in the correct order)")
    elif t == "number":
        if not isinstance(d.get("answer"), (int, float)):
            errors.append(f"{where}: number answer must be numeric")
        if not 0 <= d.get("tolerance", 0) <= 1:
            errors.append(f"{where}: tolerance is a fraction between 0 and 1")
    elif t == "recall":
        if not isinstance(d.get("answer"), str) or not d["answer"].strip():
            errors.append(f"{where}: recall needs a reference answer")
    if t != "recall" and not d.get("explain"):
        errors.append(f"{where}: needs an explain")


def check():
    errors = []
    cats = load(F / "categories.json")["categories"]
    planned = {c["id"] for cat in cats for c in cat["concepts"]}
    for path in sorted(F.glob("*.json")):
        if path.name in ("categories.json", "index.json"):
            continue
        cid = path.stem
        if cid not in planned:
            errors.append(f"fundamentals/{path.name}: not in categories.json")
            continue
        c = load(path)
        if c.get("id") != cid:
            errors.append(f"{cid}: id field must match the file name")
        if not c.get("summary"):
            errors.append(f"{cid}: missing summary")
        drills = c.get("drills") or []
        if len(drills) < 3:
            errors.append(f"{cid}: needs at least 3 drills")
        if len({d.get("type") for d in drills}) < 2:
            errors.append(f"{cid}: use at least 2 drill types")
        for i, d in enumerate(drills, 1):
            check_drill(f"{cid} drill {i}", d, errors)

    qplanned = {q["id"]: q for cat in load(Q / "categories.json")["categories"] for q in cat["questions"]}
    for q in qplanned.values():
        if q["difficulty"] not in DIFFICULTIES or not ID.fullmatch(q["id"]):
            errors.append(f"questions/categories.json: bad entry {q['id']}")
    for path in sorted(Q.glob("*.json")):
        if path.name in ("categories.json", "index.json"):
            continue
        qid = path.stem
        if qid not in qplanned:
            errors.append(f"questions/{path.name}: not in categories.json")
            continue
        q = load(path)
        if q.get("id") != qid:
            errors.append(f"{qid}: id field must match the file name")
        if not q.get("prompt"):
            errors.append(f"{qid}: missing prompt")
        ref = q.get("reference") or {}
        if set(ref) - STEPS:
            errors.append(f"{qid}: unknown reference steps {sorted(set(ref) - STEPS)}")
        missing = STEPS - set(ref)
        if missing:
            errors.append(f"{qid}: reference missing steps {sorted(missing)}")
        rubric = q.get("rubric") or []
        if len(rubric) < 6:
            errors.append(f"{qid}: rubric needs at least 6 items")
        for i, r in enumerate(rubric, 1):
            if not r.get("text") or not r.get("keywords"):
                errors.append(f"{qid} rubric {i}: needs text and keywords")
        for c in q.get("concepts", []):
            if c not in planned:
                errors.append(f"{qid}: unknown concept {c!r}")
            elif not written(F, c):
                pass  # linked before it is written; fine
    # the index must be current
    before = ((F / "index.json").read_text() if (F / "index.json").exists() else "",
              (Q / "index.json").read_text() if (Q / "index.json").exists() else "")
    build()
    after = ((F / "index.json").read_text(), (Q / "index.json").read_text())
    if before != after:
        errors.append("index.json was stale; run `python3 tools/sd.py build` and commit the result")
    for e in errors:
        print(f"ERROR {e}")
    return errors


def coverage():
    cats = load(F / "categories.json")["categories"]
    todo = [f"{cat['title']}: {c['id']}" for cat in cats for c in cat["concepts"] if not written(F, c["id"])]
    qtodo = [q["id"] for cat in load(Q / "categories.json")["categories"] for q in cat["questions"] if not written(Q, q["id"])]
    total = sum(len(cat["concepts"]) for cat in cats)
    print(f"fundamentals: {total - len(todo)} / {total} written")
    for t in todo:
        print("  todo", t)
    qtotal = sum(len(cat["questions"]) for cat in load(Q / "categories.json")["categories"])
    print(f"questions: {qtotal - len(qtodo)} / {qtotal} written")
    for t in qtodo:
        print("  todo", t)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "build":
        build()
    elif cmd == "coverage":
        coverage()
    else:
        sys.exit(1 if check() else 0)
