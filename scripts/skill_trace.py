#!/usr/bin/env python3
"""
skill_trace.py
项目级 Skill 执行轨迹（trace）记录与查询 CLI。
契约：references/skill_trace.md —— 配置、事件信封、时序与依赖约定（R1~R6）、存储与截断、CLI 输出与退出码。
默认关闭；开关读写与轨迹文件均按工程隔离：不跨工程回退，不落全局目录。
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from hs_paths import ensure_utf8_stdout

try:
    import yaml  # type: ignore
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

DEFAULT_SKILL_EXECUTION_CONFIG: Dict[str, Any] = {
    "version": "1.0",
    "description": "项目级 skill 执行配置（Skill 执行轨迹等能力开关）",
    "features": {
        "skill_trace": False,
    },
}

FEATURE_DESCRIPTIONS: Dict[str, str] = {
    "skill_trace": "Skill 执行轨迹记录（开启后按会话写入 hs_dev_docs/_06_dev_process/_05_skill_trace/sessions）",
}

CONFIG_REL_PATH = Path("config") / "skill_execution.yaml"
TRACE_SESSIONS_REL_PATH = Path("hs_dev_docs") / "_06_dev_process" / "_05_skill_trace" / "sessions"

SCHEMA_VERSION = 1
MAX_EVENT_BYTES = 8192
PREVIEW_CHARS = 4096

SESSION_START = "session_start"
SESSION_END = "session_end"

EVENT_REQUIRED_FIELDS: Dict[str, Tuple[str, ...]] = {
    SESSION_START: ("host", "cwd"),
    SESSION_END: ("reason",),
    "intent_sizing": ("intent", "change_size", "work_mode", "confirmed", "source"),
    "skill_load": ("skill_id",),
    "route_decision": ("intent", "phase", "process_skill", "functional_skills"),
    "phase_transition": ("from", "to", "status"),
    "task_link": ("task_id",),
    "key_action": ("kind", "summary", "result"),
    "decision": ("question", "adopted"),
    "deviation": ("what_happened", "correction"),
    "error_retry": ("error", "action", "attempt"),
    "timing": ("scope", "duration_ms"),
    "tool_result": ("producer", "action", "result", "facts", "source"),
}

EVENT_ENUM_FIELDS: Dict[str, Dict[str, Tuple[str, ...]]] = {
    "tool_result": {"result": ("ok", "fail"), "source": ("tool",)},
    SESSION_END: {"reason": ("completed", "aborted", "handoff", "unknown")},
    "intent_sizing": {
        "change_size": ("S", "M", "L"),
        "work_mode": ("DESIGN", "IMPLEMENT", "READONLY"),
    },
    "phase_transition": {
        "status": ("entered", "waiting_acceptance", "accepted", "blocked", "skipped"),
    },
    "key_action": {
        "kind": ("command", "test", "file", "output", "other"),
        "result": ("ok", "fail", "partial", "unknown"),
    },
    "error_retry": {"action": ("retry", "fallback", "abort", "ignored")},
}

REF_REQUIRED_EVENTS = ("task_link", "decision", "deviation")

TS_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
EVENT_ID_PATTERN = re.compile(r"^e_(\d{6})$")
SESSION_ID_PATTERN = re.compile(r"^s_\d{8}_\d{6}_[0-9a-f]{4}$")


class TraceUsageError(Exception):
    """用法或校验错误：退出码 2，拒绝写入。"""


class TraceRuntimeError(Exception):
    """运行失败（I/O 等）：退出码 1，仅告警不阻断主流程。"""


def _utc_now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def find_skill_execution_config(root: Path) -> Path:
    """定位项目级 skill 执行配置：仅目标工程 config/skill_execution.yaml（不做跨工程回退）。"""
    return Path(root).resolve() / CONFIG_REL_PATH


def load_skill_execution_config(root: Optional[Path] = None) -> Dict[str, Any]:
    """读取项目级 skill 执行配置；缺失或损坏时回落到默认（skill_trace=false）。"""
    if root is None:
        root = Path.cwd()
    root = Path(root).resolve()

    cfg_file = find_skill_execution_config(root)
    if not cfg_file.is_file():
        import copy

        data = copy.deepcopy(DEFAULT_SKILL_EXECUTION_CONFIG)
        data["config_file"] = None
        return data

    content = cfg_file.read_text(encoding="utf-8")
    parsed: Optional[Dict[str, Any]] = None
    if HAS_YAML:
        try:
            loaded = yaml.safe_load(content)
            if isinstance(loaded, dict):
                parsed = loaded
        except Exception:
            parsed = None

    if parsed is None:
        features: Dict[str, Any] = {}
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue
            key, value = line.split(":", 1)
            key = key.strip().lstrip("-").strip()
            value = value.split("#")[0].strip().lower()
            if value in ("true", "1", "yes", "on"):
                features[key] = True
            elif value in ("false", "0", "no", "off"):
                features[key] = False
        parsed = {"features": features}

    merged_features = dict(DEFAULT_SKILL_EXECUTION_CONFIG["features"])
    user_features = parsed.get("features", {})
    if isinstance(user_features, dict):
        for key, value in user_features.items():
            if key in merged_features:
                merged_features[key] = bool(value)

    return {
        "version": str(parsed.get("version", "1.0")),
        "features": merged_features,
        "config_file": str(cfg_file),
    }


def save_skill_execution_config(root: Path, config: Dict[str, Any]) -> Path:
    """持久化项目级 skill 执行配置（固定模板，逐行可兜底解析）。"""
    root = Path(root).resolve()
    cfg_file = root / CONFIG_REL_PATH
    cfg_file.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# hs-dev-skill 项目级 Skill 执行配置 (Skill Execution Config)",
        "# 开关与轨迹记录均按工程隔离；skill_trace 缺省关闭",
        f"version: \"{config.get('version', '1.0')}\"",
        "",
        "features:",
    ]
    features = config.get("features", DEFAULT_SKILL_EXECUTION_CONFIG["features"])
    for key, value in features.items():
        desc = FEATURE_DESCRIPTIONS.get(key, "")
        val_str = "true" if value else "false"
        lines.append(f"  {key}: {val_str:<5}  # {desc}")
    lines.append("")

    cfg_file.write_text("\n".join(lines), encoding="utf-8")
    return cfg_file


def is_trace_enabled(root: Optional[Path] = None) -> bool:
    """查询项目级 trace 开关；未配置即关闭。"""
    cfg = load_skill_execution_config(root)
    return bool(cfg.get("features", {}).get("skill_trace", False))


def sessions_dir(root: Path) -> Path:
    return Path(root).resolve() / TRACE_SESSIONS_REL_PATH


def _gen_session_id() -> str:
    from datetime import datetime, timezone

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    return f"s_{stamp}_{os.urandom(2).hex()}"


def _validate_event_payload(event: str, data: Dict[str, Any], ref: Optional[str]) -> List[str]:
    errors: List[str] = []
    if event not in EVENT_REQUIRED_FIELDS:
        errors.append(f"unknown_event:{event}")
        return errors
    if not isinstance(data, dict):
        errors.append("data_not_object")
        return errors
    for field in EVENT_REQUIRED_FIELDS[event]:
        if field not in data:
            errors.append(f"missing_data_field:{field}")
    for field, allowed in EVENT_ENUM_FIELDS.get(event, {}).items():
        if field in data and data[field] not in allowed:
            errors.append(f"invalid_enum:{field}")
    if event in REF_REQUIRED_EVENTS and not (ref and str(ref).strip()):
        errors.append("missing_ref")
    if event == "error_retry" and isinstance(data.get("attempt"), int) and data["attempt"] < 1:
        errors.append("invalid_attempt")
    if event == "timing" and isinstance(data.get("duration_ms"), int) and data["duration_ms"] < 0:
        errors.append("invalid_duration_ms")
    if event == "tool_result":
        if not isinstance(data.get("facts"), dict):
            errors.append("tool_facts_not_object")
        for field in ("producer", "action"):
            if not isinstance(data.get(field), str) or not data[field].strip():
                errors.append("invalid_tool_field:" + field)
    return errors


def _encode_event_line(envelope: Dict[str, Any]) -> str:
    line = json.dumps(envelope, ensure_ascii=False)
    if len(line.encode("utf-8")) <= MAX_EVENT_BYTES:
        return line

    data_json = json.dumps(envelope.get("data", {}), ensure_ascii=False)
    envelope["truncated"] = True
    envelope["data"] = {
        "truncated": True,
        "original_bytes": len(data_json.encode("utf-8")),
        "preview": "",
    }
    room = MAX_EVENT_BYTES - len(json.dumps(envelope, ensure_ascii=False).encode("utf-8")) - 16
    preview = data_json[:PREVIEW_CHARS]
    while len(preview.encode("utf-8")) > room and preview:
        preview = preview[: max(len(preview) * 3 // 4, 1)]
    envelope["data"]["preview"] = preview
    line = json.dumps(envelope, ensure_ascii=False)
    while len(line.encode("utf-8")) > MAX_EVENT_BYTES and envelope["data"]["preview"]:
        envelope["data"]["preview"] = envelope["data"]["preview"][:-64] if len(envelope["data"]["preview"]) > 64 else ""
        line = json.dumps(envelope, ensure_ascii=False)
    return line


def _append_event_line(path: Path, line: str) -> None:
    try:
        with path.open("a", encoding="utf-8", newline="\n") as f:
            f.write(line + "\n")
    except OSError as ex:
        raise TraceRuntimeError(f"write_failed:{path}:{ex}") from ex


def _session_path(root: Path, session_id: str) -> Path:
    if not SESSION_ID_PATTERN.match(session_id or ""):
        raise TraceUsageError(f"invalid_session_id:{session_id}")
    return sessions_dir(root) / f"{session_id}.jsonl"


def _line_count(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except OSError as ex:
        raise TraceRuntimeError(f"read_failed:{path}:{ex}") from ex


def start_session(root: Path, host: str = "unknown", cwd: Optional[str] = None) -> Dict[str, Any]:
    """开启一次会话：生成 session_id 并写入 session_start（R4：关闭时静默 no-op）。"""
    root = Path(root).resolve()
    if not is_trace_enabled(root):
        return {"ok": True, "skipped": "trace_disabled"}

    target_dir = sessions_dir(root)
    session_id = ""
    path: Optional[Path] = None
    for _ in range(5):
        candidate = _gen_session_id()
        candidate_path = target_dir / f"{candidate}.jsonl"
        if not candidate_path.exists():
            session_id = candidate
            path = candidate_path
            break
    if path is None:
        raise TraceRuntimeError("session_id_collision")

    try:
        target_dir.mkdir(parents=True, exist_ok=True)
    except OSError as ex:
        raise TraceRuntimeError(f"mkdir_failed:{target_dir}:{ex}") from ex

    envelope = {
        "v": SCHEMA_VERSION,
        "event_id": "e_000001",
        "session_id": session_id,
        "ts": _utc_now(),
        "event": SESSION_START,
        "data": {"host": host, "cwd": cwd or os.getcwd()},
    }
    _append_event_line(path, _encode_event_line(envelope))
    return {"ok": True, "session_id": session_id, "path": str(path), "event_id": "e_000001"}


def record_event(
    root: Path,
    session_id: str,
    event: str,
    data: Optional[Dict[str, Any]] = None,
    ref: Optional[str] = None,
) -> Dict[str, Any]:
    """向指定会话追加一条事件（R2/R3/R5/R6：会话存在、引用完整、失败降级、超限截断）。"""
    root = Path(root).resolve()
    if not is_trace_enabled(root):
        return {"ok": True, "skipped": "trace_disabled"}

    path = _session_path(root, session_id)
    if not path.is_file():
        raise TraceUsageError(f"session_not_found:{session_id}")

    event = (event or "").strip()
    payload = data if isinstance(data, dict) else {}
    errors = _validate_event_payload(event, payload, ref)
    if errors:
        raise TraceUsageError("invalid_event:" + ",".join(errors))

    next_index = _line_count(path) + 1
    envelope: Dict[str, Any] = {
        "v": SCHEMA_VERSION,
        "event_id": f"e_{next_index:06d}",
        "session_id": session_id,
        "ts": _utc_now(),
        "event": event,
        "data": payload,
    }
    if ref:
        envelope["ref"] = ref

    _append_event_line(path, _encode_event_line(envelope))
    return {"ok": True, "event_id": envelope["event_id"], "path": str(path)}


def read_session_events(path: Path) -> List[Dict[str, Any]]:
    """读取会话事件（跳过不可解析行；严格校验请用 validate_session）。"""
    events: List[Dict[str, Any]] = []
    try:
        lines = Path(path).read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as ex:
        raise TraceRuntimeError(f"read_failed:{path}:{ex}") from ex
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            events.append(parsed)
    return events


def list_session_files(root: Path) -> List[Path]:
    directory = sessions_dir(root)
    if not directory.is_dir():
        return []
    return sorted(directory.glob("*.jsonl"))


def _select_session_files(
    root: Path,
    session_id: Optional[str] = None,
    task_id: Optional[str] = None,
) -> List[Path]:
    if session_id:
        if not SESSION_ID_PATTERN.match(session_id):
            return []
        candidate = sessions_dir(root) / f"{session_id}.jsonl"
        files = [candidate] if candidate.is_file() else []
    else:
        files = list_session_files(root)
    if task_id:
        matched: List[Path] = []
        for path in files:
            for event in read_session_events(path):
                if event.get("event") == "task_link" and str(event.get("data", {}).get("task_id")) == str(task_id):
                    matched.append(path)
                    break
        files = matched
    return files


def collect_events(
    root: Path,
    session_id: Optional[str] = None,
    task_id: Optional[str] = None,
    since: Optional[str] = None,
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """按会话/任务/时间筛选事件，返回 (会话 ID 列表, 已排序事件列表)。"""
    root = Path(root).resolve()
    files = _select_session_files(root, session_id=session_id, task_id=task_id)
    ids: List[str] = []
    events: List[Dict[str, Any]] = []
    for path in files:
        ids.append(path.stem)
        for event in read_session_events(path):
            if since and str(event.get("ts", "")) < since:
                continue
            events.append(event)
    events.sort(key=lambda e: (str(e.get("ts", "")), str(e.get("session_id", "")), str(e.get("event_id", ""))))
    return ids, events


def summarize(
    root: Path,
    session_id: Optional[str] = None,
    task_id: Optional[str] = None,
    since: Optional[str] = None,
) -> Dict[str, Any]:
    ids, events = collect_events(root, session_id=session_id, task_id=task_id, since=since)
    counts: Dict[str, int] = {}
    phases: List[Dict[str, Any]] = []
    deviations: List[Dict[str, Any]] = []
    errors: List[Dict[str, Any]] = []
    for event in events:
        name = str(event.get("event", "unknown"))
        counts[name] = counts.get(name, 0) + 1
        data = event.get("data", {})
        if name == "phase_transition":
            phases.append(
                {
                    "from": data.get("from"),
                    "to": data.get("to"),
                    "status": data.get("status"),
                    "ts": event.get("ts"),
                }
            )
        elif name == "deviation":
            deviations.append(
                {
                    "what_happened": data.get("what_happened"),
                    "correction": data.get("correction"),
                    "ref": event.get("ref"),
                    "ts": event.get("ts"),
                }
            )
        elif name == "error_retry":
            errors.append(
                {
                    "error": data.get("error"),
                    "action": data.get("action"),
                    "attempt": data.get("attempt"),
                    "ts": event.get("ts"),
                }
            )
    timestamps = [str(e.get("ts", "")) for e in events if e.get("ts")]
    return {
        "ok": True,
        "sessions": ids,
        "counts": counts,
        "first_ts": min(timestamps) if timestamps else None,
        "last_ts": max(timestamps) if timestamps else None,
        "phases": phases,
        "deviations": deviations,
        "errors": errors,
    }


def validate_session(path: Path, root: Optional[Path] = None) -> Dict[str, Any]:
    """按 R1~R3 校验单个会话文件；返回 {ok, errors, warnings}。"""
    path = Path(path)
    errors: List[str] = []
    warnings: List[str] = []

    if not path.is_file():
        return {"ok": False, "errors": [f"file_not_found:{path}"], "warnings": warnings}

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as ex:
        return {"ok": False, "errors": [f"read_failed:{ex}"], "warnings": warnings}

    expected_session = path.stem
    prev_ts = ""
    valid_events: List[Dict[str, Any]] = []
    for index, line in enumerate(lines, 1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as ex:
            errors.append(f"line {index}: invalid_json:{ex.msg}")
            continue
        if not isinstance(event, dict):
            errors.append(f"line {index}: not_object")
            continue

        valid_events.append(event)
        for key in ("v", "event_id", "session_id", "ts", "event", "data"):
            if key not in event:
                errors.append(f"line {index}: missing_field:{key}")
        if event.get("session_id") != expected_session:
            errors.append(f"line {index}: session_mismatch:{event.get('session_id')}")
        expected_id = f"e_{len(valid_events):06d}"
        if event.get("event_id") != expected_id:
            errors.append(f"line {index}: event_id_out_of_sequence:{event.get('event_id')} (expected {expected_id})")
        ts = str(event.get("ts", ""))
        if not TS_PATTERN.match(ts):
            errors.append(f"line {index}: invalid_ts:{ts}")
        elif prev_ts and ts < prev_ts:
            errors.append(f"line {index}: ts_regression:{ts} < {prev_ts}")
        if ts:
            prev_ts = ts

        name = str(event.get("event", ""))
        data = event.get("data", {})
        if isinstance(data, dict) and data.get("truncated") is True:
            warnings.append(f"line {index}: payload_truncated")
        else:
            payload_errors = _validate_event_payload(name, data if isinstance(data, dict) else {}, event.get("ref"))
            for err in payload_errors:
                errors.append(f"line {index}: {err}")

        ref = event.get("ref")
        if name == "deviation" and isinstance(ref, str) and EVENT_ID_PATTERN.match(ref):
            known = {str(e.get("event_id")) for e in valid_events}
            if ref not in known:
                warnings.append(f"line {index}: unresolved_ref:{ref}")
        if name in ("task_link", "decision") and isinstance(ref, str) and ("/" in ref or "\\" in ref):
            if root is not None and not (Path(root).resolve() / ref).exists():
                warnings.append(f"line {index}: unresolved_ref:{ref}")

    if valid_events:
        if valid_events[0].get("event") != SESSION_START:
            errors.append("first_event_not_session_start")
        if valid_events[-1].get("event") != SESSION_END:
            warnings.append("last_event_not_session_end")
    else:
        warnings.append("no_events")

    return {"ok": not errors, "errors": errors, "warnings": warnings}


def _print_json(payload: Dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def main(argv: Optional[List[str]] = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="hs-dev-skill Skill 执行轨迹（trace）记录与查询")
    parser.add_argument("--root", default=None, help="Workspace root directory")
    sub = parser.add_subparsers(dest="command")

    def add_root(sub_parser: argparse.ArgumentParser) -> None:
        sub_parser.add_argument("--root", default=None, help="Workspace root directory")

    p_status = sub.add_parser("status", help="显示项目级 trace 开关状态")
    p_enable = sub.add_parser("enable", help="开启项目级 trace")
    p_disable = sub.add_parser("disable", help="关闭项目级 trace")

    p_start = sub.add_parser("start", help="开启一次 trace 会话（写入 session_start）")
    p_start.add_argument("--host", default="unknown", help="宿主标识（cursor/codex/other 等）")

    p_record = sub.add_parser("record", help="向会话追加一条事件")
    p_record.add_argument("--session", required=True, help="会话 ID（start 返回）")
    p_record.add_argument("--event", required=True, help="事件类型（详见 references/skill_trace.md §3）")
    p_record.add_argument("--ref", default=None, help="关联引用（task_link/decision/deviation 必填）")
    p_record.add_argument("--data", default=None, help="事件载荷 JSON 字符串")

    p_summary = sub.add_parser("summary", help="会话复盘摘要")
    p_summary.add_argument("--session", default=None, help="限定会话 ID")
    p_summary.add_argument("--task", default=None, help="限定任务 ID（含该 task_link 的会话）")
    p_summary.add_argument("--since", default=None, help="起始时间（YYYY-MM-DDTHH:MM:SSZ）")

    p_query = sub.add_parser("query", help="原始事件查询（NDJSON 输出）")
    p_query.add_argument("--session", default=None, help="限定会话 ID")
    p_query.add_argument("--task", default=None, help="限定任务 ID")
    p_query.add_argument("--event", default=None, help="事件类型过滤")
    p_query.add_argument("--since", default=None, help="起始时间")
    p_query.add_argument("--limit", type=int, default=None, help="最大返回事件数")

    p_validate = sub.add_parser("validate", help="按 R1~R3 校验会话文件")
    p_validate.add_argument("--session", default=None, help="会话 ID")
    p_validate.add_argument("--file", default=None, help="会话文件路径")

    for sub_parser in (p_status, p_enable, p_disable, p_start, p_record, p_summary, p_query, p_validate):
        add_root(sub_parser)

    args = parser.parse_args(argv)
    root = Path(args.root or ".").resolve()

    try:
        if args.command == "status" or not args.command:
            cfg = load_skill_execution_config(root)
            _print_json(
                {
                    "ok": True,
                    "root": str(root),
                    "enabled": bool(cfg["features"].get("skill_trace", False)),
                    "config_path": cfg.get("config_file"),
                }
            )
            return 0

        if args.command == "enable" or args.command == "disable":
            cfg = load_skill_execution_config(root)
            cfg["features"]["skill_trace"] = args.command == "enable"
            path = save_skill_execution_config(root, cfg)
            _print_json({"ok": True, "enabled": args.command == "enable", "config_path": str(path)})
            return 0

        if args.command == "start":
            _print_json(start_session(root, host=args.host))
            return 0

        if args.command == "record":
            data: Optional[Dict[str, Any]] = None
            if args.data is not None:
                try:
                    parsed = json.loads(args.data)
                except json.JSONDecodeError as ex:
                    raise TraceUsageError(f"invalid_data_json:{ex.msg}") from ex
                if not isinstance(parsed, dict):
                    raise TraceUsageError("data_not_object")
                data = parsed
            _print_json(record_event(root, args.session, args.event, data=data, ref=args.ref))
            return 0

        if args.command == "summary":
            _print_json(summarize(root, session_id=args.session, task_id=args.task, since=args.since))
            return 0

        if args.command == "query":
            _, events = collect_events(root, session_id=args.session, task_id=args.task, since=args.since)
            if args.event:
                events = [e for e in events if e.get("event") == args.event]
            if args.limit is not None:
                events = events[: max(args.limit, 0)]
            for event in events:
                print(json.dumps(event, ensure_ascii=False))
            return 0

        if args.command == "validate":
            if bool(args.session) == bool(args.file):
                raise TraceUsageError("provide_exactly_one_of:--session,--file")
            if args.session and not SESSION_ID_PATTERN.match(args.session):
                raise TraceUsageError(f"invalid_session_id:{args.session}")
            target = Path(args.file) if args.file else sessions_dir(root) / f"{args.session}.jsonl"
            result = validate_session(target, root=root)
            _print_json(result)
            return 0 if result["ok"] else 1

        parser.print_help()
        return 2
    except TraceUsageError as ex:
        print(json.dumps({"ok": False, "error": str(ex)}, ensure_ascii=False), file=sys.stderr)
        return 2
    except TraceRuntimeError as ex:
        print(json.dumps({"ok": False, "warning": str(ex)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
