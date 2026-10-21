"""Render explicitly recorded task links, without guessing missing history."""
from collections import deque
import html
import json
from pathlib import Path

from ..storage import CONTROL


def graph(root, task_id, limit=1000):
    if not task_id:
        raise ValueError("Task ID is required")
    if not 1 <= limit <= 5000:
        raise ValueError("Graph limit must be between 1 and 5000")
    rows = deque(maxlen=limit)
    count = 0
    folder = Path(root) / CONTROL / "trace"

    def rotation(path):
        return 0 if path.name == "events.jsonl" else int(path.name.split(".")[1])

    for path in sorted(folder.glob("events*.jsonl"), key=rotation, reverse=True):
        with path.open() as stream:
            for line in stream:
                row = json.loads(line)
                if row.get("attributes", {}).get("task_id") == task_id:
                    rows.append(row)
                    count += 1
    nodes = [{"id": r["event_id"], "event": r["event"], "timestamp": r["timestamp"],
              "run_id": r["run_id"], "operation_id": r.get("operation_id"),
              "attributes": r.get("attributes", {})} for r in rows]
    edges = []
    for row in rows:
        for field, kind in (("previous_event_id", "next"), ("parent_event_id", "contains"),
                            ("retry_of_event_id", "retry")):
            if row.get(field):
                edges.append({"source": row[field], "target": row["event_id"], "kind": kind})
    known = {n["id"] for n in nodes}
    missing = sorted({e["source"] for e in edges} - known)
    return {"task_id": task_id, "nodes": nodes, "edges": edges, "missing_event_ids": missing,
            "truncated": count > limit, "coverage": "retained_events_only",
            "history_complete": False,
            "unlinked_event_ids": [r["event_id"] for r in rows if "previous_event_id" not in r]}


def mermaid(value):
    aliases = {n["id"]: f"n{i}" for i, n in enumerate(value["nodes"])}
    for key in value["missing_event_ids"]:
        aliases[key] = f"n{len(aliases)}"
    lines = ["flowchart TD", "  %% Observed retained events only; missing history is not reconstructed."]
    for node in value["nodes"]:
        attrs = node["attributes"]
        parts = [node["event"]]
        for key in ("activity_id", "stage_id", "outcome", "check_id", "name", "source_path",
                    "duration_ms", "retry_count", "context_chars"):
            if attrs.get(key) is not None:
                parts.append(f"{key}: {attrs[key]}")
        label = "<br/>".join(html.escape(str(p), quote=True).replace("\n", " ").replace("\r", " ") for p in parts)
        lines.append(f'  {aliases[node["id"]]}["{label}"]')
    for key in value["missing_event_ids"]:
        lines.append(f'  {aliases[key]}["unavailable event"]')
    for edge in value["edges"]:
        arrow = "-.->" if edge["kind"] == "contains" else "-->"
        lines.append(f'  {aliases[edge["source"]]} {arrow}|{edge["kind"]}| {aliases[edge["target"]]}')
    return "\n".join(lines)
