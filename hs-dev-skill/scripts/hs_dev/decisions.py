"""Project-level decision ledger. Append-only and hash-chained; decisions outlive task retention.

The ledger is the single authority for decision rationale: task directories record
acceptance state, this ledger records what was decided, against which document
revisions, and what it superseded. Doc content established by an entry is digest
bound, so later edits surface as stale instead of silently diverging.
"""

import json
from pathlib import Path

from .storage import atomic, identifier, local, now, read_json, sha
from .indexing.units import resolve_units

LEDGER = "hs_dev_docs/foundation/decisions.jsonl"
OVERVIEW = "hs_dev_docs/foundation/decisions.md"
EVENTS = {"accepted", "superseded"}
ACTORS = {"human", "model"}
STATUS_LABELS = {"current": "现行", "stale": "内容已变化", "superseded": "已推翻"}


def ledger_path(root):
    return local(root, LEDGER)


def entry_digest(entry):
    return sha(json.dumps(entry, sort_keys=True, ensure_ascii=False).encode())


def _field_problems(entry, seen):
    problems = []
    if entry.get("schema_version") != 1:
        problems.append("unsupported schema_version")
    decision_id = entry.get("decision_id")
    if not isinstance(decision_id, str) or not decision_id.strip():
        problems.append("missing decision_id")
    elif decision_id in seen:
        problems.append("duplicate decision_id: " + decision_id)
    if entry.get("event") not in EVENTS:
        problems.append("unknown event")
    if entry.get("actor") not in ACTORS:
        problems.append("unknown actor")
    for key in ("title", "scope", "confirmation", "reason", "recorded_at"):
        if not isinstance(entry.get(key), str):
            problems.append("missing " + key)
    if entry.get("event") == "accepted" and not entry.get("title", "").strip():
        problems.append("missing title")
    for key in ("task_id", "activity", "supersedes", "previous_digest"):
        if entry.get(key) is not None and not isinstance(entry[key], str):
            problems.append("invalid " + key)
    if entry.get("event") == "superseded" and not entry.get("supersedes"):
        problems.append("superseding entry requires supersedes")
    if not isinstance(entry.get("alternatives"), list) or any(not isinstance(a, str) for a in entry.get("alternatives", [])):
        problems.append("invalid alternatives")
    for key in ("units", "describes"):
        rows = entry.get(key)
        if not isinstance(rows, list):
            problems.append("invalid " + key)
            continue
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("unit_id"), str):
                problems.append("invalid " + key + " row")
            elif not isinstance(row.get("unit_revision"), str):
                problems.append("invalid " + key + " unit_revision")
    rows = entry.get("outputs")
    if not isinstance(rows, list):
        problems.append("invalid outputs")
    else:
        for row in rows:
            if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                problems.append("invalid outputs row")
            else:
                digest = row.get("digest")
                if digest is not None and (not isinstance(digest, str) or len(digest) != 64):
                    problems.append("invalid output digest")
    return problems


def read_entries(root):
    """Validate and load the ledger; any tampering or drift raises."""
    path = ledger_path(root)
    if not path.exists():
        return []
    entries, seen, by_id, superseded, previous = [], set(), {}, set(), None
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            raise ValueError(f"Decision ledger has a blank line at {number}")
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"Decision ledger is corrupt at line {number}: {error}")
        problems = _field_problems(entry, seen)
        if entry.get("previous_digest") != previous:
            problems.append("chain break")
        target = by_id.get(entry.get("supersedes"))
        if entry.get("event") == "superseded":
            if target is None:
                problems.append("supersedes unknown decision")
            elif target["event"] != "accepted":
                problems.append("supersedes a non-accepted entry")
            elif target["decision_id"] in superseded:
                problems.append("decision superseded twice: " + target["decision_id"])
        if problems:
            raise ValueError(f"Decision ledger invalid at line {number}: " + "; ".join(problems))
        previous = entry_digest(entry)
        if entry["event"] == "superseded":
            superseded.add(entry["supersedes"])
        seen.add(entry["decision_id"])
        by_id[entry["decision_id"]] = entry
        entries.append(entry)
    return entries


def validate(root):
    try:
        entries = read_entries(root)
    except ValueError as error:
        return {"ok": False, "errors": [str(error)], "count": 0, "digest": None}
    return {"ok": True, "errors": [], "count": len(entries),
            "digest": entry_digest(entries[-1]) if entries else None}


def statuses(root, entries):
    superseded = {e["supersedes"] for e in entries if e.get("supersedes")}
    unit_ids = sorted({u["unit_id"] for e in entries for u in e["units"]}
                      | {u["unit_id"] for e in entries for u in e.get("describes", [])})
    current = {}
    if unit_ids:
        try:
            current = resolve_units(root, unit_ids)
        except (ValueError, OSError):
            current = {}

    def drifted(entry, key):
        return any(current.get(u["unit_id"], {}).get("unit_revision") != u["unit_revision"]
                   for u in entry.get(key, []))

    result = {}
    for entry in entries:
        if entry["event"] == "superseded":
            result[entry["decision_id"]] = "superseding"
        elif entry["decision_id"] in superseded:
            result[entry["decision_id"]] = "superseded"
        elif drifted(entry, "units") or drifted(entry, "describes"):
            result[entry["decision_id"]] = "stale"
        else:
            result[entry["decision_id"]] = "current"
    return result


def describes_bindings(root, paths):
    """Bind the code files that registered objects declare as described by these doc paths.

    Doc metadata relations (kind='describes') point at object registry ids; each
    object carries the code path it names. Binding their revisions lets a later
    code change stale the decision that documented it — the reverse direction of
    the digest chain.
    """
    graph = read_json(Path(root) / "hs_dev_docs/foundation/object_graph.json")
    objects = graph.get("objects") if isinstance(graph, dict) else None
    if not objects:
        return []
    targets = set()
    from .indexing.engine import Index
    with Index(root) as index:
        for path in sorted({str(p) for p in paths}):
            for row in index.connect().execute(
                    "SELECT DISTINCT target FROM relations WHERE path=? AND kind='describes'", (path,)):
                targets.add(row[0])
    if not targets:
        return []
    code_paths = sorted({o["path"] for o in objects
                         if isinstance(o, dict) and o.get("id") in targets
                         and isinstance(o.get("path"), str) and o["path"].strip()})
    bindings = []
    for path in code_paths:
        unit_id = "file:" + path
        try:
            resolved = resolve_units(root, [unit_id])[unit_id]
        except (ValueError, OSError):
            continue
        bindings.append({"unit_id": unit_id, "unit_revision": resolved["unit_revision"]})
    return bindings


def append_entry(root, entry):
    """Validate the existing chain, bind unit revisions, append and republish."""
    entries = read_entries(root)
    if entry.get("units"):
        unit_ids = [u["unit_id"] for u in entry["units"]]
        try:
            resolved = resolve_units(root, unit_ids)
        except (ValueError, OSError) as error:
            raise ValueError("Decision unit references cannot be resolved: " + str(error))
        missing = [u["unit_id"] for u in entry["units"] if u["unit_id"] not in resolved]
        if missing:
            raise ValueError("Unknown decision unit reference: " + ", ".join(missing))
        for unit in entry["units"]:
            unit["unit_revision"] = resolved[unit["unit_id"]]["unit_revision"]
    entry = {"schema_version": 1, "decision_id": "D" + identifier(), "recorded_at": now(),
             "alternatives": [], "units": [], "outputs": [], "describes": [], "supersedes": None,
             "task_id": None, "activity": None, **entry,
             "previous_digest": entry_digest(entries[-1]) if entries else None}
    problems = _field_problems(entry, {e["decision_id"] for e in entries})
    if problems:
        raise ValueError("Invalid decision entry: " + "; ".join(problems))
    path = ledger_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    atomic(path, existing + json.dumps(entry, ensure_ascii=False) + "\n")
    refresh(root, entries + [entry])
    from .indexing.engine import Index
    with Index(root) as index:
        index.publish()
    return entry


def record(root, title, reason, actor, confirmation, scope="project", task_id=None,
           activity=None, alternatives=(), unit_ids=(), supersedes=None):
    if not title.strip() or not confirmation.strip() or actor not in ACTORS:
        raise ValueError("Decision record requires a title, an actor and a real confirmation")
    if supersedes:
        entries = read_entries(root)
        target = next((e for e in entries if e["decision_id"] == supersedes), None)
        if target is None or target["event"] != "accepted":
            raise ValueError("Supersede target must be an accepted decision: " + supersedes)
    paths = set()
    if unit_ids:
        try:
            resolved = resolve_units(root, list(unit_ids))
        except (ValueError, OSError) as error:
            raise ValueError("Decision unit references cannot be resolved: " + str(error))
        paths = {resolved[u]["path"] for u in unit_ids if u in resolved}
    return append_entry(root, {"event": "accepted", "title": title, "reason": reason, "actor": actor,
                               "confirmation": confirmation, "scope": scope, "task_id": task_id,
                               "activity": activity, "alternatives": list(alternatives),
                               "units": [{"unit_id": u, "unit_revision": ""} for u in unit_ids],
                               "describes": describes_bindings(root, paths),
                               "supersedes": supersedes})


def supersede(root, decision_id, reason, actor, confirmation, task_id=None):
    entries = read_entries(root)
    target = next((e for e in entries if e["decision_id"] == decision_id), None)
    if target is None or target["event"] != "accepted":
        raise ValueError("Supersede target must be an accepted decision: " + decision_id)
    if decision_id in {e["supersedes"] for e in entries if e.get("supersedes")}:
        raise ValueError("Decision already superseded: " + decision_id)
    return append_entry(root, {"event": "superseded", "title": "推翻 " + decision_id, "reason": reason,
                               "actor": actor, "confirmation": confirmation, "scope": target["scope"],
                               "task_id": task_id or target.get("task_id"), "supersedes": decision_id})


def record_approval(root, task, scope, approval, units=(), outputs=(), material_paths=()):
    """Promote one scope approval into the durable ledger at approval time."""
    return append_entry(root, {"event": "accepted", "title": "验收通过：" + scope,
                               "reason": "", "actor": approval["actor"],
                               "confirmation": approval["confirmation"], "scope": scope,
                               "task_id": task["task_id"],
                               "activity": task["current_activity"] if task["mode"] == "activity" else None,
                               "units": list(units), "outputs": list(outputs),
                               "describes": describes_bindings(root, material_paths)})


def missing_scopes(root, task):
    scopes = task["activities"] if task["mode"] == "activity" else sorted({a[0] for a in task["activities"]})
    recorded = {e["scope"] for e in read_entries(root)
                if e["event"] == "accepted" and e.get("task_id") == task["task_id"]}
    return [scope for scope in scopes if scope not in recorded]


def view(root):
    entries = read_entries(root)
    state = statuses(root, entries)
    rows = [{**entry, "status": state[entry["decision_id"]]} for entry in entries]
    return {"entries": rows, "count": len(entries),
            "stale_count": sum(1 for row in rows if row["status"] == "stale"),
            "superseded_count": sum(1 for row in rows if row["status"] == "superseded"),
            "digest": entry_digest(entries[-1]) if entries else None}


def refresh(root, entries=None):
    """Regenerate the human-readable ledger overview after every append."""
    if entries is None:
        entries = read_entries(root)
    state = statuses(root, entries)
    lines = ['<!-- hs: {"id": "foundation-decisions", "kind": "decisions", "tags": ["decisions"], "tier": "warm"} -->',
             "# 决策台账", "",
             "项目级权威决策记录，只增不改；推翻以新记录标注，历史不删除。当前内容与决策绑定摘要不一致时标记为“内容已变化”。", ""]
    if not entries:
        lines.append("暂无决策记录。")
    for entry in entries:
        if entry["event"] == "superseded":
            lines.append(f"- {entry['decision_id']} · {entry['recorded_at']} · 推翻 {entry['supersedes']}：{entry['reason'] or '未说明'}")
            continue
        label = STATUS_LABELS[state[entry["decision_id"]]]
        actor = "人工" if entry["actor"] == "human" else "模型"
        lines.append(f"- {entry['decision_id']} · {label} · {actor} · {entry['recorded_at']} · {entry['title']}")
        lines.append(f"  范围：{entry['scope']}" + (f" · 来源任务：{entry['task_id']}" if entry.get("task_id") else ""))
        if entry["reason"]:
            lines.append("  理由：" + entry["reason"])
        for alternative in entry["alternatives"]:
            lines.append("  否决方案：" + alternative)
        for unit in entry["units"]:
            lines.append(f"  绑定文档：{unit['unit_id']} @ {unit['unit_revision'][:12]}")
        for described in entry.get("describes", []):
            lines.append(f"  描述代码：{described['unit_id']} @ {described['unit_revision'][:12]}")
        for output in entry["outputs"]:
            lines.append(f"  交付物：{output['path']} @ {(output['digest'] or '缺失')[:12]}")
    lines.extend(["", f"记录数：{len(entries)}" +
                  (f" · 台账摘要：{entry_digest(entries[-1])[:12]}" if entries else ""), ""])
    atomic(local(root, OVERVIEW), "\n".join(lines))
