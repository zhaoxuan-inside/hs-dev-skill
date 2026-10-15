#!/usr/bin/env python3
"""Read-only routing for the bundled process and functional skills (stdlib only)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from hs_paths import ensure_utf8_stdout


def load_registry(root: Path) -> Dict[str, Any]:
    path = root / "resources" / "skill_routes.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _local_file(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        raise ValueError("Registry path escapes bundle: " + relative)
    if not path.is_file():
        raise ValueError("Missing bundle file: " + relative)
    return path


def validate_registry(root: Path, registry: Dict[str, Any]) -> None:
    if registry.get("schema_version") != 1:
        raise ValueError("Unsupported skill route schema")
    entries = registry.get("skills", [])
    ids = set()
    owners: Dict[str, str] = {}
    for entry in entries:
        name = entry["id"]
        if name in ids:
            raise ValueError("Duplicate skill: " + name)
        ids.add(name)
        if entry["axis"] not in ("process", "functional"):
            raise ValueError("Unknown skill axis: " + name)
        content = _local_file(root, entry["path"]).read_text(encoding="utf-8")
        if not re.match(r"^---\s*\nname:\s*" + re.escape(name) + r"\s*\n", content):
            raise ValueError("Skill name mismatch: " + name)
        for relative in entry.get("references", []):
            _local_file(root, relative)
            if relative in owners:
                raise ValueError("Multiple reference owners: " + relative)
            owners[relative] = name
    by_id = {entry["id"]: entry for entry in entries}
    registered_paths = {entry["path"] for entry in entries}
    actual_paths = {p.relative_to(root).as_posix() for p in (root / "skills").glob("*/SKILL.md")}
    if registered_paths != actual_paths:
        raise ValueError("Child skill registration mismatch: " + repr(sorted(registered_paths ^ actual_paths)))
    for axis, routes in (("process", registry["intents"]),
                         ("process", registry["phases"]),
                         ("process", registry["events"]),
                         ("functional", registry["domains"])):
        for target in routes.values():
            if target not in by_id or by_id[target]["axis"] != axis:
                raise ValueError("Invalid route target: " + target)
    if set(registry["phases"]) != set("0123456"):
        raise ValueError("BUILD phases must cover 0 through 6")
    for phase, domains in registry.get("default_domains", {}).items():
        if phase not in registry["phases"] or any(d not in registry["domains"] for d in domains):
            raise ValueError("Invalid default domains for phase: " + phase)
    for relative in registry.get("shared_references", []):
        _local_file(root, relative)
        if relative in owners:
            raise ValueError("Shared reference also has a skill owner: " + relative)
        owners[relative] = "shared"
    expected = {p.relative_to(root).as_posix() for p in (root / "references").glob("*.md")}
    if expected != set(owners):
        raise ValueError("Reference ownership mismatch: " + repr(sorted(expected ^ set(owners))))


def route(root: Path, registry: Dict[str, Any], intent: str,
          phase: Optional[int] = None, domains: Sequence[str] = (),
          event: Optional[str] = None) -> Dict[str, Any]:
    """Return a route plan, never execute a skill, change state, or grant acceptance."""
    if intent not in registry["intents"]:
        raise ValueError("Unknown intent: " + intent)
    if phase is not None and str(phase) not in registry["phases"]:
        raise ValueError("Unknown phase: " + str(phase))
    if event and event not in registry["events"]:
        raise ValueError("Unknown event: " + event)
    if intent == "EXPLORE" and event:
        raise ValueError("Read-only exploration cannot request change or delivery acceptance")
    if intent == "BUILD" and phase is None:
        raise ValueError("BUILD requires an explicit current phase (0-6)")
    if intent not in ("BUILD", "RESUME") and phase is not None:
        raise ValueError("Phase 0-6 applies to BUILD or restored RESUME context only")
    selected = list(dict.fromkeys(domains))
    for domain in selected:
        if domain not in registry["domains"]:
            raise ValueError("Unknown functional domain: " + domain)
    if event:
        primary = registry["events"][event]
    elif intent == "BUILD":
        primary = registry["phases"][str(phase)]
    else:
        primary = registry["intents"][intent]
    # Restored state must be read before choosing a continuation stage.
    if intent == "BUILD" and not event and not selected:
        selected = registry.get("default_domains", {}).get(str(phase), [])
    if intent == "EXPLORE":
        mode = "READONLY"
    elif event == "change" or (intent == "BUILD" and phase is not None and phase <= 4):
        mode = "DESIGN"
    else:
        mode = None if intent == "RESUME" else "IMPLEMENT"
    by_id = {entry["id"]: entry for entry in registry["skills"]}

    def descriptor(name: str) -> Dict[str, Any]:
        entry = by_id[name]
        return {"id": name, "axis": entry["axis"], "path": entry["path"],
                "absolute_path": str(_local_file(root, entry["path"])),
                "references": entry.get("references", [])}

    return {"ok": True, "bundle_root": str(root.resolve()), "intent": intent,
            "phase": phase, "event": event, "work_mode": mode,
            "process_skill": descriptor(primary),
            "functional_skills": [descriptor(registry["domains"][d]) for d in selected],
            "read_only": intent == "EXPLORE",
            "requires_context_restore": intent == "RESUME",
            "stage_accepted": False,
            "note": "Route only. Read current inputs and acceptance records before execution; "
                    "restore RESUME state before routing its next stage."}


def main(argv: Optional[Sequence[str]] = None) -> int:
    ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent,
                        help="Complete installed hs-dev-skill bundle root, not project cwd")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Validate child skills, routes, and reference ownership")
    sub.add_parser("list", help="List process and functional skills without loading their bodies")
    p_route = sub.add_parser("route", help="Emit a read-only route plan")
    p_route.add_argument("--intent", required=True)
    p_route.add_argument("--phase", type=int)
    p_route.add_argument("--domains", nargs="*", default=[])
    p_route.add_argument("--event", choices=["change", "acceptance"])
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        registry = load_registry(root)
        validate_registry(root, registry)
        if args.command == "check":
            result = {"ok": True, "skills": len(registry["skills"]),
                      "references": sum(len(e.get("references", [])) for e in registry["skills"])
                      + len(registry.get("shared_references", []))}
        elif args.command == "list":
            result = {"ok": True, "skills": [{k: e[k] for k in ("id", "axis", "path", "scope")}
                                               for e in registry["skills"]]}
        else:
            result = route(root, registry, args.intent, args.phase, args.domains, args.event)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
