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
        concepts = [{"id": c["id"], "title": c["title"], "prompts": len(load(F / f"{c['id']}.json").get("prompts") or [])}
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


def check_concept(cid, c, errors):
    for field in ("explain", "model"):
        if not isinstance(c.get(field), str) or not c[field].strip():
            errors.append(f"{cid}: missing {field}")
    details = c.get("details") or []
    if not 4 <= len(details) <= 8:
        errors.append(f"{cid}: needs 4-8 details")
    for i, d in enumerate(details, 1):
        if not d.get("q") or not d.get("a"):
            errors.append(f"{cid} detail {i}: needs q and a")
    prompts = c.get("prompts") or []
    if not 2 <= len(prompts) <= 4:
        errors.append(f"{cid}: needs 2-4 prompts")
    for i, p in enumerate(prompts, 1):
        if not p.get("q") or not 3 <= len(p.get("points") or []) <= 7:
            errors.append(f"{cid} prompt {i}: needs q and 3-7 points")
    leftover = {"summary", "drills"} & set(c)
    if leftover:
        errors.append(f"{cid}: old quiz fields {sorted(leftover)} must be removed")


def check():
    errors = []
    cats = load(F / "categories.json")["categories"]
    planned = {c["id"] for cat in cats for c in cat["concepts"]}
    titles = {c["id"]: c["title"] for cat in cats for c in cat["concepts"]}
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
        check_concept(cid, c, errors)
        if c.get("title") != titles.get(cid):
            errors.append(f"{cid}: title must match categories.json ({titles.get(cid)!r})")

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
