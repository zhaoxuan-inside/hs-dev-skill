"""Evidence-bound development cycles with serial, recoverable source ownership."""
from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
import subprocess
import os
import signal
import time
import selectors
import re
from urllib.parse import quote
from . import __version__, knowledge, templates
from .store import PROJECT, DELIVERIES, EXECUTION, path, read, write, hash_file, inventory, digest, now, uid, transaction, contained

CONTROL = EXECUTION + "/workspace.json"
STATE_DIR = EXECUTION + "/deliveries/"
SOURCE_REGISTRY = knowledge.SOURCES
RESULTS = {"supported", "not-applicable", "unknown", "conflict"}


def _json(value):
    if isinstance(value, str):
        return json.loads(Path(value[1:]).read_text()) if value.startswith("@") else json.loads(value)
    return value


def _text(value, label):
    return templates.concrete(value, label)


def _source_inventory(root):
    return {p: h for p, h in inventory(root).items() if p != SOURCE_REGISTRY and not (p.startswith(DELIVERIES + "/") and "history" in Path(p).parts)}


def _control(root):
    state = read(path(root, CONTROL))
    if not state or state.get("version") != __version__:
        raise ValueError("Workspace is uninitialized or incompatible; do not migrate or replace existing state silently")
    if digest(state["policy"]) != state.get("policy_digest"):
        raise ValueError("Workspace policy changed outside initialization")
    return state


def _file(root, delivery):
    if not isinstance(delivery, str) or not re.fullmatch(r"d-[0-9a-f]{16}", delivery):
        raise ValueError("Invalid delivery id")
    return path(root, STATE_DIR + delivery + ".json")


def _load(root, delivery):
    value = read(_file(root, delivery))
    if not value or value.get("id") != delivery or value.get("version") != __version__:
        raise ValueError("Unknown delivery")
    if value["catalog_digest"] != templates.verify_catalog()["digest"]:
        raise ValueError("Activity catalog changed; preserve the old delivery and explicitly replan")
    return value


def _story(state):
    def link(record):
        relative = os.path.relpath(record["path"], DELIVERIES + "/" + state["id"])
        return "[" + record["id"] + "](" + quote(relative, safe="/.-_") + ")：" + record["path"]
    lines = ["# " + state["title"], "", "交付：" + state["id"], "范围：" + state["scope"],
             "当前活动：" + state["activity"], "", "## 当前沟通与反例", ""]
    for q in state["questions"].values():
        if q.get("cycle", 0) != state.get("cycle", 0):
            continue
        lines += ["### " + q["id"] + " " + q["question"], q["reason"], "建议：" + q["recommendation"]]
        lines += ["阻断当前活动：" + str(q.get("blocking", True)), "影响范围：" + q.get("affected_work", "当前活动")]
        if q.get("resolution"):
            r = q["resolution"]
            lines += ["问题处置：" + r["outcome"] + "；" + r["reason"], "来源：" + ", ".join(r["bindings"])]
        elif q.get("answer"):
            lines += ["回答理解：" + q["answer"]["understanding"], "来源：" + ", ".join(q["answer"]["bindings"])]
        else:
            lines += ["未取得回答：" + ("当前活动受阻。" if q.get("blocking", True) else "当前活动可继续，依赖答案的范围不放行。")]
        if q.get("reflection"):
            r = q["reflection"]
            lines += ["反例：" + r["scenario"], r["outcome"] + "：" + r["reason"]]
        lines += [""]
    prior = _prior_questions(state)
    if prior:
        lines += ["## 历史未决问题", ""]
        lines += [q["id"] + "：" + q["question"] + "；影响：" + q.get("affected_work", "需重新评估") for q in prior]
    assessment = state.get("assessment")
    if assessment:
        record = assessment["record"]
        lines += ["## 当前理解与缺口", "", record["understanding"], record["dialogue"]["summary"]]
        lines += [u["issue"] + "；下一动作：" + u["next_action"] for u in record["unknowns"]]
    if state.get("plan"):
        lines += ["", "## 实施计划（方案与行为依据见活动成果）", "", "计划摘要：" + state["plan"]["digest"]]
        lines += [step["id"] + "：" + step["action"] + "；预期：" + step["expected"] for step in state["plan"]["record"]["steps"]]
        lines += ["恢复：" + state["plan"]["record"]["recovery"]["strategy"]]
    lines += ["", "## 已登记的活动成果", ""]
    for output in state["outputs"].values():
        r = output["record"]
        lines += [link(r) + "；可提交：" + str(output["ready"])]
    for cycle in state["cycles"]:
        lines += ["前序活动 " + cycle["activity"] + "：" + cycle.get("status", "submitted")]
        if cycle.get("assessment"):
            lines += ["当时理解（复用前核验来源）：" + cycle["assessment"]["record"]["understanding"]]
        lines += [link(o["record"]) for o in cycle["outputs"].values()]
    lines += ["", "本摘要仅组织真实登记内容；源变更后须通过readiness/resume重核，不独立证明业务事实。", ""]
    return "\n".join(lines)


def _save(root, state):
    state["updated_at"] = now()
    relative = DELIVERIES + "/" + state["id"] + "/story.md"
    file = path(root, relative)
    actual = hash_file(file)
    pending = state.get("story_pending")
    allowed = {state.get("story_digest")}
    if pending:
        allowed.update([pending["before"], pending["after"]])
    if actual not in allowed:
        raise ValueError("Generated delivery summary changed externally; preserve and reconcile it explicitly")
    content = _story(state)
    after = digest(content.encode())
    if actual != after:
        if file.is_file():
            write(path(root, DELIVERIES + "/" + state["id"] + "/history/" + uid("story-") + ".md"), file.read_bytes())
        state["story_pending"] = {"before": actual, "after": after}
        write(_file(root, state["id"]), state)
        write(file, content)
        state.pop("story_pending", None)
        state["verification"] = None
    state["story_digest"] = after
    if "expected" in state:
        state["expected"][relative] = after
    write(_file(root, state["id"]), state)


def _audit(root, state, event, details=None):
    file = path(root, STATE_DIR + state["id"] + ".events.json")
    rows = read(file, [])
    rows.append({"time": now(), "event": event, "activity": state["activity"], "details": details or {}})
    write(file, rows)


def _mutable(state):
    if state["status"] not in {"active", "locked"}:
        raise ValueError("Delivery is submitted/rolled back; unlock before advancing to a new activity")


def _sources(root, ids, scope, claim=None, state=None):
    if not isinstance(ids, list) or not ids or len(ids) != len(set(ids)) or not all(isinstance(s, str) for s in ids):
        raise ValueError("Nonempty unique source_ids are required")
    result = {}
    for source_id in ids:
        source = knowledge.source_state(root, source_id)
        if not source["usable"]:
            frozen = (state or {}).get("input_sources", {}).get(source_id)
            owned = frozen and source.get("record_digest") == frozen.get("record_digest") and source.get("issues") == ["Evidence snapshot content drifted"] \
                and source.get("path") in (state or {}).get("touched", []) \
                and hash_file(path(root, source["path"])) == state["tracked"].get(source["path"]) \
                and source.get("digest") == frozen.get("digest")
            if not owned:
                raise ValueError("Source is not usable: " + source_id + " " + "; ".join(source["issues"]))
        if source["scope"] not in {scope, "project"}:
            raise ValueError("Source scope does not cover this delivery: " + source_id)
        if claim and (source["kind"] != "user" or source["claim_type"] not in (claim if isinstance(claim, (tuple, list, set)) else {claim})):
            raise ValueError("A genuine user " + str(claim) + " source is required")
        result[source_id] = {"record_digest": source["record_digest"], "scope": source["scope"]}
    return result


def _current_sources(root, bindings, scope, state=None):
    current = _sources(root, list(bindings), scope, state=state)
    if current != bindings:
        raise ValueError("Evidence record, version or scope changed; reassess affected judgments")


def _prior_questions(state):
    return [q for q in state["questions"].values()
            if q.get("cycle", 0) != state.get("cycle", 0) and not q.get("resolution")
            and not (q.get("answer") and q.get("reflection", {}).get("outcome") == "supported")]


def _questions_ready(root, state):
    questions = [q for q in state["questions"].values() if q.get("cycle", 0) == state.get("cycle", 0)]
    for q in questions:
        if q.get("resolution"):
            _current_sources(root, q["resolution"]["bindings"], state["scope"], state)
            continue
        if not q.get("blocking", True):
            continue
        answer, reflection = q.get("answer"), q.get("reflection")
        if not answer or not reflection or reflection["outcome"] != "supported":
            raise ValueError("Question requires a sourced answer and supported scenario reflection: " + q["id"])
        _current_sources(root, answer["bindings"], state["scope"], state)
        _current_sources(root, reflection["bindings"], state["scope"], state)
        if reflection["answer_digest"] != digest(answer):
            raise ValueError("Answer changed after reflection: " + q["id"])
    return questions + _prior_questions(state)


def _judgments(root, records, expected, scope, label, state=None):
    if not isinstance(records, list) or len(records) != len(expected) or {r.get("id") for r in records if isinstance(r, dict)} != set(expected):
        raise ValueError(label + " must judge every fixed criterion exactly once")
    bindings, ready = {}, True
    for row in records:
        if row.get("status") not in RESULTS:
            raise ValueError(label + " status must be supported/not-applicable/unknown/conflict")
        _text(row.get("judgment"), row["id"] + " judgment")
        if row["status"] in {"supported", "not-applicable"}:
            bindings.update(_sources(root, row.get("source_ids"), scope, state=state))
        if row["status"] != "supported":
            _text(row.get("reason"), row["id"] + " reason")
            _text(row.get("next_action"), row["id"] + " next action")
        ready = ready and row["status"] in {"supported", "not-applicable"}
    return bindings, ready


def _readiness(root, state):
    try:
        questions = _questions_ready(root, state)
        assessment = state.get("assessment")
        if not assessment or assessment["activity"] != state["activity"]:
            raise ValueError("Assess the activity entry conditions before planning")
        _current_sources(root, assessment["bindings"], state["scope"], state)
        if assessment["question_digest"] != digest(questions):
            raise ValueError("Discussion changed after assessment")
        if not assessment["ready"]:
            raise ValueError("Entry conditions or declared blocking unknowns remain unresolved")
        return {"ok": True, "delivery": state["id"], "activity": state["activity"], "scope": state["scope"],
                "entry_ready": True, "output_ready": False, "meaning": "Entry conditions are ready, not implementation or delivery completion"}
    except ValueError as error:
        return {"ok": False, "delivery": state["id"], "activity": state["activity"], "entry_ready": False, "issues": [str(error)]}


def _ready(root, state):
    result = _readiness(root, state)
    if not result["ok"]:
        raise ValueError("; ".join(result["issues"]))


def _discussion_digest(state):
    return digest({"activity": state["activity"], "scope": state["scope"], "questions": state["questions"], "assessment": state.get("assessment")})


def _plan_valid(root, state):
    plan = state.get("plan")
    if not plan or plan["activity"] != state["activity"]:
        raise ValueError("Current activity plan missing")
    _ready(root, state)
    _current_sources(root, plan["bindings"], state["scope"], state)
    if plan["discussion_digest"] != _discussion_digest(state):
        raise ValueError("Understanding or discussion changed; replace the plan explicitly")
    return plan


def _authorized(root, state, control):
    plan = _plan_valid(root, state)
    policy = control["policy"]
    effects = plan["record"]["effects"]
    high_risk = effects["external"] or effects["irreversible"] or not effects["local_reversible"]
    paths = plan["record"]["paths"]
    if policy["mode"] == "read-only" and any(not p.startswith(knowledge.EVIDENCE) for p in paths):
        raise ValueError("Read-only policy does not authorize source or document changes")
    accepted = state.get("authorization")
    if accepted and accepted["plan_digest"] == plan["digest"]:
        _current_sources(root, accepted["bindings"], state["scope"], state)
        return "existing-user-authorization"
    if policy["mode"] == "bounded" and not high_risk and all(any(contained(p, prefix) for prefix in policy["allow"]) for p in paths):
        source = policy.get("source")
        if not source or hash_file(path(root, source["path"])) != source["digest"]:
            raise ValueError("Bounded policy authorization source missing or changed")
        return "bounded-policy"
    raise ValueError("Plan requires a current user decision authorization bound to plan_digest")


def _reconcile_pending(root, state):
    pending = state.get("pending")
    if not pending:
        return
    actual = hash_file(path(root, pending["path"]))
    if actual not in {pending["before"], pending["after"]}:
        raise ValueError("Interrupted write conflicts with an external edit: " + pending["path"])
    if actual == pending["after"]:
        _update_expected(state, pending["path"], actual)
        if pending["path"] not in state["touched"]:
            state["touched"].append(pending["path"])
    state.pop("pending", None)
    _save(root, state)


def _update_expected(state, relative, current):
    state["tracked"][relative] = current
    if not relative.startswith(EXECUTION + "/"):
        if current is None:
            state["expected"].pop(relative, None)
        else:
            state["expected"][relative] = current


def _locked(root, state, *, allow_stale=False):
    control = _control(root)
    lock = control.get("lock")
    if not lock or lock["delivery"] != state["id"] or lock["token"] != state.get("lock_token") or state["status"] != "locked":
        raise ValueError("A matching active delivery lock is required")
    _reconcile_pending(root, state)
    if not allow_stale:
        _authorized(root, state, control)
        if _source_inventory(root) != state["expected"]:
            raise ValueError("Sources changed outside the managed cycle; resume/reconcile or rollback without overwriting others")
        for relative, expected in state["tracked"].items():
            if hash_file(path(root, relative)) != expected:
                raise ValueError("Planned file changed outside the managed cycle: " + relative)
    return control


def _allowed_path(root, relative, *, execution_output=False):
    file = path(root, relative)
    if Path(relative).as_posix() != relative:
        raise ValueError("Use a canonical contained relative path")
    parts = Path(relative).parts
    if any(p in {".git", "node_modules", ".venv", "venv"} for p in parts) or relative == SOURCE_REGISTRY:
        raise ValueError("Dependency, Git and source registry controls are not editable output paths")
    if relative.startswith(DELIVERIES + "/") and (relative.endswith("/story.md") or "history" in parts):
        raise ValueError("Delivery summary and history are program-owned")
    if relative == EXECUTION or relative.startswith(EXECUTION + "/"):
        if not execution_output or not relative.startswith(knowledge.EVIDENCE):
            raise ValueError("Execution controls are program-owned; only declared evidence outputs are allowed")
    if file.is_dir():
        raise ValueError("Plan exact files, not directories")
    return file


def _apply(root, state, changes, *, execution_output=False):
    _locked(root, state)
    if not isinstance(changes, dict) or not changes:
        raise ValueError("Changes must map planned file paths to UTF-8 text or null")
    for relative, content in changes.items():
        if relative not in state["plan"]["record"]["paths"]:
            raise ValueError("Write is outside the exact planned paths: " + relative)
        _allowed_path(root, relative, execution_output=execution_output)
        if content is not None and not isinstance(content, str):
            raise ValueError("Only UTF-8 text changes or explicit deletion are supported")
        if content is not None and len(content.encode()) > 4_000_000:
            raise ValueError("Single change exceeds the supported 4 MB bound")
    changed = []
    for relative, content in sorted(changes.items()):
        file = path(root, relative)
        after = digest(content.encode()) if content is not None else None
        before = hash_file(file)
        if before == after:
            continue
        state["pending"] = {"path": relative, "before": before, "after": after}
        _save(root, state)
        if content is None:
            file.unlink(missing_ok=True)
        else:
            write(file, content)
        _update_expected(state, relative, after)
        if relative not in state["touched"]:
            state["touched"].append(relative)
        state.pop("pending", None)
        state["verification"] = None
        _save(root, state)
        changed.append(relative)
    _audit(root, state, "apply", {"paths": changed})
    return {"ok": True, "delivery": state["id"], "changed": changed}


def _output(root, state, record, *, produce=False):
    _locked(root, state)
    if record.get("scope") != state["scope"]:
        raise ValueError("Output scope must equal the fixed delivery scope")
    bindings = {}
    def validate_sources(ids):
        bindings.update(_sources(root, ids, state["scope"], state=state))
    for row in record.get("answers", []) + record.get("acceptance", []):
        for source_id in row.get("source_ids", []):
            source = knowledge.source_state(root, source_id)
            if not source["usable"] and row.get("basis") != "baseline":
                raise ValueError("Changed input can only support an explicitly baseline judgment; register a fresh source for current facts")
    spec, ready = templates.validate_output(state["activity"], record, validate_sources)
    relative = record.get("path")
    if not isinstance(relative, str) or relative not in state["plan"]["record"]["paths"]:
        raise ValueError("Output path must be an exact planned file")
    prefixes = {"project": PROJECT + "/", "delivery": DELIVERIES + "/" + state["id"] + "/", "execution": knowledge.EVIDENCE + state["id"] + "/"}
    native = not produce and record.get("format") == "artifact"
    if not relative.startswith(prefixes[spec["layer"]]) and not (native and spec["layer"] == "project" and not relative.startswith("hs-dev/")):
        raise ValueError("Output must live in its declared information layer: " + spec["layer"])
    file = _allowed_path(root, relative, execution_output=spec["layer"] == "execution")
    if produce:
        text = file.read_text() if file.is_file() else ""
        _apply(root, state, {relative: templates.insert(text, spec, record)}, execution_output=spec["layer"] == "execution")
    if not file.is_file():
        raise ValueError("Output file does not exist; use produce or managed apply")
    section = file.read_bytes() if native else templates.section(file.read_text(), spec["id"]).encode()
    if native and record.get("artifact_digest") != digest(section):
        raise ValueError("Native artifact digest does not match the actual file")
    if not native and section.decode() != templates.render(spec, record):
        raise ValueError("Actual output section does not match its structured answers and judgments")
    state["outputs"][record["id"]] = {"record": copy.deepcopy(record), "bindings": bindings,
                                          "section_digest": digest(section), "native": native, "ready": ready}
    _save(root, state)
    _audit(root, state, "produce" if produce else "record-output", {"id": record["id"], "path": relative, "ready": ready})
    return {"ok": True, "id": record["id"], "path": relative, "ready": ready, "section_digest": digest(section)}


def _outputs_valid(root, state):
    expected = {o["id"] for o in templates.contract(state["activity"])["outputs"]}
    if set(state["outputs"]) != expected:
        raise ValueError("Every activity output must be recorded exactly once")
    for output in state["outputs"].values():
        if not output["ready"]:
            raise ValueError("Output has unresolved/unknown acceptance judgments")
        _current_sources(root, output["bindings"], state["scope"], state)
        record = output["record"]
        file = path(root, record["path"])
        section = (file.read_bytes() if output.get("native") else templates.section(file.read_text(), record["id"]).encode()) if file.is_file() else b""
        if digest(section) != output["section_digest"]:
            raise ValueError("Output content changed after recording: " + record["id"])


def _policy(root, record):
    raw = record.get("policy", record) if isinstance(record, dict) else {}
    if not raw:
        return {"mode": "confirm", "allow": [], "source": None}
    if set(raw) - {"mode", "allow", "source"} or raw.get("mode") not in {"confirm", "bounded", "read-only"}:
        raise ValueError("Policy requires mode confirm/bounded/read-only, allow prefixes and an actual source")
    allow = raw.get("allow", [])
    if not isinstance(allow, list) or len(allow) != len(set(allow)):
        raise ValueError("Policy allow must be unique contained path prefixes")
    for prefix in allow:
        path(root, prefix)
        if prefix == "hs-dev" or contained(EXECUTION, prefix) or (contained(prefix, EXECUTION) and not contained(prefix, knowledge.EVIDENCE.rstrip("/"))):
            raise ValueError("Policy cannot authorize execution controls")
    source = raw.get("source")
    if source:
        if not isinstance(source, dict) or set(source) != {"path", "digest"} or hash_file(path(root, source["path"])) != source["digest"] or source["digest"] is None:
            raise ValueError("Policy source must bind an actual pre-existing instruction snapshot and its digest")
    if raw["mode"] != "confirm" and not source:
        raise ValueError("Non-default policy requires a concrete authorization/settings source")
    return {"mode": raw["mode"], "allow": allow, "source": source}


def _init(root, args):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Project root must already exist")
    if any((root / old).exists() for old in ("hs-dev-docs", "hs-dev-runtime", "hs_dev_docs")):
        raise ValueError("Old workspace format is not migrated automatically")
    existing = root / "hs-dev"
    if existing.exists():
        allowed = {"execution/index.sqlite", "execution/index-manifest.json", "execution/knowledge.lock"}
        files = {p.relative_to(existing).as_posix() for p in existing.rglob("*") if p.is_file()}
        directories = {p.relative_to(existing).as_posix() for p in existing.rglob("*") if p.is_dir()}
        manifest = read(root / knowledge.MANIFEST, {})
        if not files or files - allowed or directories - {"execution"} or manifest.get("parser_version") != knowledge.PARSER_VERSION:
            raise ValueError("Existing hs-dev data will not be replaced; only a recognized derived-only index can be initialized")
        if any(p.is_symlink() for p in existing.rglob("*")):
            raise ValueError("Existing workspace contains a symlink")
    policy = _policy(root, _json(args.get("record")) or {})
    for relative in (PROJECT, DELIVERIES, EXECUTION):
        path(root, relative).mkdir(parents=True, exist_ok=True)
    initial = {"version": __version__, "policy": policy, "policy_digest": digest(policy), "lock": None, "created_at": now()}
    with path(root, CONTROL).open("x", encoding="utf-8") as stream:
        json.dump(initial, stream, ensure_ascii=False, indent=2)
        stream.flush()
        os.fsync(stream.fileno())
    return {"ok": True, "version": __version__, "policy": policy, "knowledge": knowledge.reindex(root)}


def _status(root):
    control = _control(root)
    states = [read(p) for p in sorted(path(root, STATE_DIR).glob("*.json")) if not p.name.endswith(".events.json")]
    return {"ok": True, "version": __version__, "policy": control["policy"], "lock": control.get("lock"),
            "deliveries": [{"id": s["id"], "activity": s["activity"], "scope": s["scope"], "status": s["status"],
                            "prior_questions": _prior_questions(s)} for s in states]}


def _execute(root, command, args):
    control = _control(root)
    if command == "status":
        return _status(root)
    if command == "start":
        title, scope = _text(args.get("title"), "Delivery title"), _text(args.get("scope"), "Delivery scope")
        activity = templates.activity(args.get("activity"))
        state = {"version": __version__, "id": uid("d-"), "title": title, "scope": scope, "activity": activity["id"],
                 "catalog_digest": templates.verify_catalog()["digest"], "status": "active", "created_at": now(),
                 "questions": {}, "outputs": {}, "cycles": [], "assessment": None, "plan": None,
                 "authorization": None, "verification": None, "touched": []}
        _save(root, state)
        _audit(root, state, "start")
        return {"ok": True, "delivery": state["id"], "activity": state["activity"], "scope": scope, "template": templates.contract(activity["id"])}
    state = _load(root, args.get("delivery"))
    if command == "readiness":
        return _readiness(root, state)
    if command == "resume":
        if state.get("story_pending"):
            _save(root, state)
        if state["status"] == "locking":
            own = control.get("lock")
            if own and (own["delivery"] != state["id"] or own["token"] != state["lock_token"]):
                raise ValueError("Another lock owns the workspace; no takeover")
            if not own:
                if _source_inventory(root) != state["expected"]:
                    raise ValueError("Lock acquisition was interrupted and source changed; no automatic takeover")
                control["lock"] = {"delivery": state["id"], "token": state["lock_token"], "paths": list(state["tracked"]), "locked_at": now()}
                write(path(root, CONTROL), control)
            state["status"] = "locked"
            _save(root, state)
        if state["status"] == "locked":
            _locked(root, state, allow_stale=True)
            drift = _source_inventory(root) != state["expected"] or any(hash_file(path(root, p)) != h for p, h in state["tracked"].items())
            readiness = _readiness(root, state)
        else:
            drift, readiness = False, _readiness(root, state)
        return {"ok": not drift, "delivery": state["id"], "status": state["status"], "source_drift": drift,
                "readiness": readiness, "questions": state["questions"], "assessment": state.get("assessment"),
                "plan": state.get("plan"), "outputs": list(state["outputs"]), "prior_questions": _prior_questions(state),
                "next_action": "Review drift; preserve others' edits and rollback only owned paths" if drift else "Continue the existing delivery and activity"}
    if command == "unlock":
        if state["status"] not in {"submitted", "rolled-back"}:
            raise ValueError("Unlock only after consistency submit or verified rollback")
        lock = control.get("lock")
        if lock and (lock["delivery"] != state["id"] or lock["token"] != state.get("lock_token")):
            raise ValueError("No matching delivery lock to release")
        if not lock and not state.get("unlock_intent"):
            raise ValueError("No matching lock or interrupted unlock to finish")
        if state["status"] == "submitted":
            commit = state.get("commit")
            if not commit or hash_file(path(root, commit["path"])) != commit["digest"]:
                raise ValueError("Submitted consistency record is missing or changed")
        drift = _source_inventory(root) != state["expected"] or any(hash_file(path(root, p)) != h for p, h in state["tracked"].items())
        state["unlock_intent"] = True
        state["post_submit_drift"] = drift
        _save(root, state)
        control["lock"] = None
        write(path(root, CONTROL), control)
        state["unlocked_at"] = now()
        _save(root, state)
        _audit(root, state, "unlock", {"post_submit_drift": drift})
        return {"ok": True, "delivery": state["id"], "status": state["status"], "lock_released": True,
                "post_submit_drift": drift, "meaning": "Later edits are preserved and are not covered by the earlier verification"}
    if command == "advance":
        if state["status"] not in {"submitted", "rolled-back"} or control.get("lock") and control["lock"]["delivery"] == state["id"]:
            raise ValueError("Advance only after submitted activity has been unlocked")
        activity = templates.activity(args.get("activity"))
        if activity["id"] == state["activity"] and state["status"] != "rolled-back":
            raise ValueError("Choose the next actual activity, not a duplicate cycle")
        state["cycles"].append({"activity": state["activity"], "stage": state["activity"][0], "outputs": state["outputs"],
                                "assessment": state.get("assessment"), "verification": state.get("verification"), "completed_at": now(), "status": state["status"]})
        state.update(activity=activity["id"], status="active", outputs={}, assessment=None, plan=None,
                     authorization=None, verification=None, touched=[])
        state["cycle"] = state.get("cycle", 0) + 1
        for key in ("snapshot", "tracked", "expected", "lock_token", "pending", "unlocked_at", "input_sources", "commit", "unlock_intent", "post_submit_drift") :
            state.pop(key, None)
        _save(root, state)
        _audit(root, state, "advance")
        return {"ok": True, "delivery": state["id"], "activity": state["activity"], "prior_cycles": len(state["cycles"]),
                "prior_questions": _prior_questions(state), "next_action": "Assess prior unanswered questions against this activity before planning"}
    _mutable(state)
    if command == "question":
        qid = _text(args.get("id"), "Question id")
        if qid in state["questions"]:
            raise ValueError("Question id already exists; keep prior conversation")
        options = _json(args.get("options"))
        if options is not None and (not isinstance(options, list) or not all(isinstance(x, str) and x.strip() for x in options)):
            raise ValueError("Question options must be concrete strings")
        blocking = args.get("blocking", True)
        if type(blocking) is not bool:
            raise ValueError("Question blocking must be a boolean")
        affected = args.get("affected_work")
        nonblocking_reason = args.get("nonblocking_reason")
        if not blocking:
            _text(affected, "Nonblocking question affected work")
            _text(nonblocking_reason, "Why current activity is independent of this answer")
        state["questions"][qid] = {"id": qid, "activity": state["activity"], "cycle": state.get("cycle", 0), "question": _text(args.get("question"), "Actual question"),
                                   "reason": _text(args.get("reason"), "Question impact"), "options": options or [],
                                   "recommendation": _text(args.get("recommendation"), "Recommendation and tradeoff"), "created_at": now(),
                                   "blocking": blocking, "affected_work": affected or "当前活动", "nonblocking_reason": nonblocking_reason}
        state["assessment"] = None
        _save(root, state)
        return {"ok": True, "question": state["questions"][qid], "next_action": "Present this question to its responsible person; no answer is implied"}
    if command == "question-resolve":
        record = _json(args.get("record"))
        if not isinstance(record, dict):
            raise ValueError("Question resolution requires a record")
        q = state["questions"].get(record.get("question_id"))
        if not q or (q.get("cycle", 0) != state.get("cycle", 0) and q not in _prior_questions(state)):
            raise ValueError("Unknown current-activity question")
        if record.get("outcome") not in {"invalid-premise", "withdrawn"}:
            raise ValueError("Resolve only an invalid-premise or withdrawn question")
        reason = _text(record.get("reason"), "Actual decision and why the question no longer applies")
        bindings = _sources(root, record.get("source_ids"), state["scope"], "decision", state)
        if any(knowledge.source_state(root, sid)["kind"] != "user" for sid in bindings):
            raise ValueError("Question resolution needs an actual user decision source")
        q["resolution"] = {"outcome": record["outcome"], "reason": reason, "bindings": bindings, "recorded_at": now()}
        state["assessment"] = None
        _save(root, state)
        _audit(root, state, "question-resolve", {"question_id": q["id"], "resolution": q["resolution"]})
        return {"ok": True, "question": q, "meaning": "Question retained; no answer or product acceptance is implied"}
    if command in {"answer", "reflect"}:
        qid = args.get("question_id") or args.get("id")
        q = state["questions"].get(qid)
        if not q or (q.get("cycle", 0) != state.get("cycle", 0) and q not in _prior_questions(state)):
            raise ValueError("Unknown current-activity question")
        ids = args.get("source")
        ids = ids.split(",") if isinstance(ids, str) else ids
        bindings = _sources(root, ids, state["scope"], ("fact", "requirement", "decision") if command == "answer" else None, state)
        if command == "answer":
            q["answer"] = {"understanding": _text(args.get("understanding"), "Answer understanding"), "bindings": bindings, "recorded_at": now()}
            q.pop("reflection", None)
            q.pop("resolution", None)
        else:
            if not q.get("answer") or args.get("outcome") not in {"supported", "reopen"}:
                raise ValueError("Reflect an actual answer with supported/reopen outcome")
            _current_sources(root, q["answer"]["bindings"], state["scope"], state)
            q["reflection"] = {"scenario": _text(args.get("scenario"), "Counterexample/scenario"), "outcome": args["outcome"],
                               "reason": _text(args.get("reason"), "Reflection reasoning"), "bindings": bindings, "answer_digest": digest(q["answer"])}
        state["assessment"] = None
        _save(root, state)
        return {"ok": True, "question": q}
    if command == "assess":
        record = _json(args.get("record"))
        if not isinstance(record, dict):
            raise ValueError("Assessment must be an object")
        _text(record.get("understanding"), "Concrete understanding")
        dialogue = record.get("dialogue")
        if not isinstance(dialogue, dict) or dialogue.get("mode") not in {"asked", "reuse"}:
            raise ValueError("Assessment requires explicit dialogue mode asked/reuse")
        _text(dialogue.get("summary"), "Dialogue/reuse explanation")
        bindings = _sources(root, dialogue.get("source_ids"), state["scope"], state=state)
        questions = _questions_ready(root, state)
        if dialogue["mode"] == "asked" and not any(q.get("resolution") or (q.get("answer") and q.get("reflection")) for q in questions):
            raise ValueError("Asked dialogue needs actual current answered/reflected questions")
        minimum = {r["id"] for r in templates.contract(state["activity"])["minimum"]}
        judged, ready = _judgments(root, record.get("entries"), minimum, state["scope"], "Entry assessment", state)
        bindings.update(judged)
        prior = _prior_questions(state)
        reviews = record.get("prior_questions", [])
        if (not isinstance(reviews, list) or len(reviews) != len(prior)
                or {r.get("id") for r in reviews if isinstance(r, dict)} != {q["id"] for q in prior}):
            raise ValueError("Assess every prior unanswered question's dependency on this activity")
        for review in reviews:
            if type(review.get("blocks")) is not bool:
                raise ValueError("Prior question review needs an explicit blocks boolean")
            _text(review.get("reason"), "Prior question dependency reason")
            _text(review.get("next_action"), "Prior question next action")
            ready = ready and not review["blocks"]
        unknowns = record.get("unknowns")
        if not isinstance(unknowns, list):
            raise ValueError("Assessment must explicitly list unknowns (possibly empty)")
        for unknown in unknowns:
            _text(unknown.get("issue"), "Unknown issue")
            _text(unknown.get("next_action"), "Unknown follow-up")
            if type(unknown.get("blocks")) is not bool:
                raise ValueError("Each unknown explicitly declares blocks true/false")
            ready = ready and not unknown["blocks"]
        state["assessment"] = {"activity": state["activity"], "record": record, "bindings": bindings,
                               "question_digest": digest(questions), "ready": ready}
        _save(root, state)
        return _readiness(root, state)
    if command == "plan":
        if state["status"] == "locked":
            raise ValueError("Do not replace a locked plan; finish or restore the owned changes first")
        _ready(root, state)
        record = _json(args.get("record"))
        if not isinstance(record, dict):
            raise ValueError("Plan must be an object")
        paths = record.get("paths")
        if not isinstance(paths, list) or not paths or len(paths) > 128 or len(paths) != len(set(paths)):
            raise ValueError("Plan requires unique exact file paths")
        for relative in paths:
            _allowed_path(root, relative, execution_output=relative.startswith(knowledge.EVIDENCE + state["id"] + "/"))
        steps, covered = record.get("steps"), set()
        if not isinstance(steps, list) or not steps or len(steps) > 256:
            raise ValueError("Plan requires executable steps")
        for step in steps:
            _text(step.get("id"), "Step id")
            _text(step.get("action"), "Step action")
            _text(step.get("expected"), "Step observable result")
            if not isinstance(step.get("paths"), list) or not step["paths"] or not set(step["paths"]).issubset(paths):
                raise ValueError("Each step must identify its exact planned paths")
            covered.update(step["paths"])
        if covered != set(paths):
            raise ValueError("Every planned path needs an execution step")
        checks = record.get("verifications")
        if not isinstance(checks, list) or not checks or len(checks) > 64:
            raise ValueError("Plan requires 1 to 64 actual verification commands")
        check_ids = []
        for check in checks:
            check_ids.append(_text(check.get("id"), "Verification id"))
            _argv(check.get("argv"))
            _text(check.get("expected"), "Verification expected result")
            _check_timeout(check)
        if sum(_check_timeout(check) for check in checks) > 3600:
            raise ValueError("Planned verification time budgets must total at most 3600 seconds")
        if len(check_ids) != len(set(check_ids)):
            raise ValueError("Verification ids must be unique")
        recovery = record.get("recovery")
        if not isinstance(recovery, dict):
            raise ValueError("Plan requires recovery strategy and limits")
        _text(recovery.get("strategy"), "Recovery strategy")
        _text(recovery.get("limitations"), "Recovery limitations")
        if not isinstance(record.get("risks"), list) or not record["risks"]:
            raise ValueError("Plan requires explicit risks or bounded-effect analysis")
        for risk in record["risks"]:
            _text(risk, "Plan risk/boundary")
        effects = record.get("effects")
        if not isinstance(effects, dict) or set(effects) != {"external", "irreversible", "local_reversible"} or any(type(v) is not bool for v in effects.values()):
            raise ValueError("Plan declares external/irreversible/local_reversible boolean effects")
        feasibility = record.get("feasibility")
        if not isinstance(feasibility, dict) or feasibility.get("status") != "supported":
            raise ValueError("Plan feasibility must be supported by actual sources")
        _text(feasibility.get("judgment"), "Plan feasibility judgment")
        bindings = _sources(root, feasibility.get("source_ids"), state["scope"], state=state)
        bindings.update(_sources(root, record.get("source_ids"), state["scope"], state=state))
        value = {"activity": state["activity"], "scope": state["scope"], "record": record, "bindings": bindings,
                 "discussion_digest": _discussion_digest(state),
                 "baseline": {p: hash_file(path(root, p)) for p in paths}}
        value["digest"] = digest(value)
        state.update(plan=value, authorization=None, verification=None)
        _save(root, state)
        return {"ok": True, "delivery": state["id"], "plan_digest": value["digest"], "paths": paths}
    if command == "authorize":
        plan = _plan_valid(root, state)
        if args.get("plan_digest") != plan["digest"]:
            raise ValueError("Authorize the actual current plan digest")
        ids = args.get("source")
        ids = ids.split(",") if isinstance(ids, str) else ids
        bindings = _sources(root, ids, state["scope"], "decision", state)
        state["authorization"] = {"plan_digest": plan["digest"], "bindings": bindings, "recorded_at": now()}
        _save(root, state)
        return {"ok": True, "delivery": state["id"], "plan_digest": plan["digest"], "source_ids": list(bindings)}
    if command == "lock":
        if control.get("lock"):
            raise ValueError("Workspace has a live serial source lock; resume its owner, do not steal it")
        _authorized(root, state, control)
        if any(hash_file(path(root, p)) != h for p, h in state["plan"]["baseline"].items()):
            raise ValueError("Planned files changed after planning; reassess and replan")
        tracked, snapshot, snapshot_size = {}, {}, 0
        for relative in state["plan"]["record"]["paths"]:
            file = path(root, relative)
            snapshot_size += file.stat().st_size if file.is_file() else 0
            if snapshot_size > 32_000_000:
                raise ValueError("Planned preimages exceed the 32 MB recovery bound; split the activity")
            tracked[relative] = hash_file(file)
            snapshot[relative] = base64.b64encode(file.read_bytes()).decode() if file.is_file() else None
        bindings = dict(state["assessment"]["bindings"])
        bindings.update(state["plan"]["bindings"])
        for q in _questions_ready(root, state):
            if q.get("resolution"):
                bindings.update(q["resolution"]["bindings"])
            elif q.get("cycle", 0) == state.get("cycle", 0) and q.get("blocking", True):
                bindings.update(q["answer"]["bindings"])
                bindings.update(q["reflection"]["bindings"])
        if state.get("authorization"):
            bindings.update(state["authorization"]["bindings"])
        state["input_sources"] = {sid: knowledge.source_state(root, sid) for sid in bindings}
        token = uid("L")
        state.update(status="locking", lock_token=token, expected=_source_inventory(root), tracked=tracked, snapshot=snapshot, touched=[], verification=None)
        _save(root, state)
        control["lock"] = {"delivery": state["id"], "token": token, "paths": list(tracked), "locked_at": now()}
        write(path(root, CONTROL), control)
        state["status"] = "locked"
        _save(root, state)
        _audit(root, state, "lock", {"paths": list(tracked)})
        return {"ok": True, "delivery": state["id"], "token": token, "coordination": "serial-workspace-write-lock"}
    if command == "apply":
        return _apply(root, state, _json(args.get("changes")))
    if command in {"produce", "record-output", "record_output"}:
        return _output(root, state, _json(args.get("record")), produce=command == "produce")
    if command == "run":
        _locked(root, state)
        checks = _json(args.get("checks"))
        expected = {c["id"]: c for c in state["plan"]["record"]["verifications"]}
        if checks is None:
            checks = list(expected.values())
        if not isinstance(checks, list) or len(checks) != len(expected):
            raise ValueError("Run every planned verification exactly once")
        commands = []
        for index, check in enumerate(checks):
            item = check if isinstance(check, dict) else {"id": list(expected)[index], "argv": check}
            if item.get("id") not in expected or item.get("argv") != expected[item["id"]]["argv"]:
                raise ValueError("Run commands must match the exact authorized verification plan")
            _argv(item["argv"])
            planned = expected[item["id"]]
            if "timeout_seconds" in item and _check_timeout(item) != _check_timeout(planned):
                raise ValueError("Run time budgets must match the authorized verification plan")
            commands.append(planned)
        if len({c["id"] for c in commands}) != len(expected):
            raise ValueError("Verification ids cannot be duplicated")
        state["verification"] = None
        _save(root, state)
        before = _source_inventory(root)
        controls_before = _control_inventory(root)
        tracked = {p: hash_file(path(root, p)) for p in state["tracked"]}
        rows = []
        folder = path(root, knowledge.EVIDENCE + state["id"] + "/" + uid("run-"))
        folder.mkdir(parents=True)
        run_deadline = time.monotonic() + 3600
        for check in commands:
            log = folder / (str(len(rows)) + ".log")
            started = time.monotonic()
            timeout = _check_timeout(check)
            code = _run_check(check["argv"], root, log, timeout_seconds=timeout, overall_deadline=run_deadline)
            rows.append({"id": check["id"], "argv": check["argv"], "expected": expected[check["id"]]["expected"],
                         "timeout_seconds": timeout, "elapsed_seconds": round(time.monotonic()-started, 3),
                         "exit_code": code, "path": log.relative_to(root).as_posix(), "digest": hash_file(log)})
        if controls_before != _control_inventory(root):
            raise ValueError("Verification changed execution controls or source registry; inspect retained evidence before recovery")
        unchanged = before == _source_inventory(root) and all(hash_file(path(root, p)) == h for p, h in tracked.items())
        value = {"ok": unchanged and all(r["exit_code"] == 0 for r in rows), "plan_digest": state["plan"]["digest"],
                 "sources": before, "tracked": tracked, "results": rows, "checked_at": now(), "unchanged": unchanged}
        state["verification"] = value
        _save(root, state)
        _audit(root, state, "run", {"ok": value["ok"], "results": rows})
        return value
    if command == "submit":
        _locked(root, state)
        _outputs_valid(root, state)
        result = state.get("verification")
        if not result or not result["ok"] or result["plan_digest"] != state["plan"]["digest"]:
            raise ValueError("Current planned verification has not passed")
        if result["sources"] != _source_inventory(root) or any(hash_file(path(root, p)) != h for p, h in result["tracked"].items()):
            raise ValueError("Outputs or sources changed after verification; run current checks again")
        for row in result["results"]:
            if hash_file(path(root, row["path"])) != row["digest"]:
                raise ValueError("Verification evidence changed")
        _ready(root, state)
        knowledge.reindex(root)
        commit = {"delivery": state["id"], "cycle": state.get("cycle", 0), "activity": state["activity"],
                  "scope": state["scope"], "plan": state["plan"], "outputs": state["outputs"],
                  "verification": result, "files": state["expected"], "submitted_at": now()}
        commit_file = path(root, STATE_DIR + state["id"] + "/commits/" + uid("commit-") + ".json")
        write(commit_file, commit)
        state["commit"] = {"path": commit_file.relative_to(root).as_posix(), "digest": hash_file(commit_file)}
        state["status"] = "submitted"
        state["submitted_at"] = now()
        _save(root, state)
        _audit(root, state, "submit")
        return {"ok": True, "delivery": state["id"], "activity": state["activity"], "status": "submitted", "lock_released": False,
                "task_complete": False,
                "next_action": "Unlock, compare remaining work with the user's objective, and continue authorized independent work; activity submission is not a stopping condition",
                "meaning": "Current activity is consistently submitted; overall task completion is not established; no Git commit or deployment is implied"}
    if command == "rollback":
        _locked(root, state, allow_stale=True)
        record = _json(args.get("record")) or {}
        preserve = record.get("preserve", [])
        if not isinstance(preserve, list) or len(preserve) != len(set(preserve)) or not set(preserve).issubset(state["touched"]):
            raise ValueError("Preserved external edits must be unique touched paths")
        if preserve:
            _text(record.get("reason"), "Reason for preserving later external edits")
            decision = _sources(root, record.get("source_ids"), state["scope"], "decision", state)
            state["preserved_external"] = {"paths": {p: hash_file(path(root, p)) for p in preserve}, "reason": record["reason"], "bindings": decision}
        for relative in state["touched"]:
            if relative not in preserve and hash_file(path(root, relative)) != state["tracked"][relative]:
                raise ValueError("Rollback would overwrite an external edit: " + relative)
        for relative in state["touched"]:
            if relative in preserve:
                _update_expected(state, relative, hash_file(path(root, relative)))
                continue
            file = path(root, relative)
            snapshot = state["snapshot"][relative]
            state["pending"] = {"path": relative, "before": hash_file(file), "after": digest(base64.b64decode(snapshot)) if snapshot is not None else None}
            _save(root, state)
            if snapshot is None:
                file.unlink(missing_ok=True)
            else:
                write(file, base64.b64decode(snapshot))
            if hash_file(file) != (digest(base64.b64decode(snapshot)) if snapshot is not None else None):
                raise ValueError("Rollback restoration failed: " + relative)
            _update_expected(state, relative, hash_file(file))
            state.pop("pending", None)
            _save(root, state)
        state["status"] = "rolled-back"
        state["verification"] = None
        _save(root, state)
        knowledge.reindex(root)
        _audit(root, state, "rollback")
        return {"ok": True, "delivery": state["id"], "status": "rolled-back", "lock_released": False,
                "limitations": "Only owned local files were restored; explicitly preserved external edits and external effects were not reverted", "preserved_external": preserve}
    raise ValueError("Unsupported engine command: " + command)


def _control_inventory(root):
    result = {SOURCE_REGISTRY: hash_file(path(root, SOURCE_REGISTRY))}
    folder = path(root, EXECUTION)
    for file in folder.rglob("*"):
        relative = file.relative_to(root).as_posix()
        if file.is_file() and not file.is_symlink() and not relative.startswith(knowledge.EVIDENCE) and file.name not in {"control.lock", "knowledge.lock"}:
            result[relative] = hash_file(file)
    return result


def _check_timeout(check):
    seconds = check.get("timeout_seconds", 30)
    if type(seconds) is not int or not 1 <= seconds <= 300:
        raise ValueError("Verification timeout_seconds must be an integer in 1..300")
    return seconds


def _run_check(argv, root, log, *, timeout_seconds=30, overall_deadline=None):
    limit, deadline = 4_000_000, time.monotonic() + _check_timeout({"timeout_seconds": timeout_seconds})
    if overall_deadline is not None:
        deadline = min(deadline, overall_deadline)
    if time.monotonic() >= deadline:
        write(log, "Verification run time budget exhausted; command was not started.\n")
        return 124
    try:
        process = subprocess.Popen(argv, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False, start_new_session=True)
    except OSError as error:
        write(log, str(error))
        return 127
    total, failure = 0, None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        with log.open("wb") as stream:
            while selector.get_map():
                if time.monotonic() >= deadline:
                    failure = 124
                    break
                for key, _ in selector.select(0.05):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    stream.write(data[:max(0, limit-total)])
                    total += len(data)
                    if total > limit:
                        failure = 125
                        break
                if failure:
                    break
            if failure:
                os.killpg(process.pid, signal.SIGKILL)
            return failure if failure else process.wait(timeout=max(0.1, deadline-time.monotonic()))
    except (subprocess.TimeoutExpired, ProcessLookupError):
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        return failure or 124
    finally:
        selector.close()
        process.stdout.close()
        if process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        process.wait()


def _argv(value):
    if not isinstance(value, list) or not value or len(value) > 128 or sum(len(str(a)) for a in value) > 131072 or any(not isinstance(a, str) or not a or "\x00" in a for a in value):
        raise ValueError("Checks require bounded nonempty argv arrays, never shell strings")


def dispatch(root, command, args):
    root = Path(root).resolve()
    if not isinstance(args, dict):
        raise ValueError("Command arguments must be an object")
    if command == "init":
        return _init(root, args)
    if command == "template":
        return templates.contract(args["activity"], args.get("output"))
    if command == "catalog-check":
        return templates.verify_catalog()
    if command in {"source-add", "reindex", "locate", "read"}:
        _control(root)
        if command == "source-add":
            return knowledge.register_source(root, _json(args["record"]))
        if command == "reindex":
            return knowledge.reindex(root)
        if command == "locate":
            return knowledge.locate(root, args["query"], args.get("limit", 5), args.get("max_bytes", 12000))
        return knowledge.read_unit(root, args["path"], args.get("start", 1), args.get("end"), args.get("digest"), args.get("max_bytes", 24000))
    _control(root)
    with transaction(root):
        return _execute(root, command, args)
