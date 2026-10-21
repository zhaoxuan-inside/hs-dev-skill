"""Semantic, complete, version-checked context delivery."""
import json
import time
from contextlib import nullcontext
from pathlib import Path

from .config import resolve
from .indexing.engine import Index, PUBLICATION, fingerprint
from .indexing.semantic import file_id
from .storage import CONTROL, local, read_json, sha
from .workspace import Workspace
from .context_budget import Budget, encode


class ReadBudgetExceeded(ValueError):
    pass


class ContextProvider:
    def __init__(self, root, index=None, resident=None):
        self.root, self.index, self.resident = Path(root).resolve(), index, resident

    def obtain(self, request):
        started = time.monotonic()
        activity = None
        if not isinstance(request, dict) or set(request) - {"goal", "task_id", "selectors", "query", "budget", "held", "delivery"}:
            raise ValueError("Invalid context request fields")
        if len(encode(request).encode()) > 65_536:
            raise ValueError("Context request too large")
        for key in ("goal", "query"):
            if key in request and (not isinstance(request[key], str) or len(request[key]) > 1024):
                raise ValueError("Invalid context " + key)
        task_id = request.get("task_id")
        if task_id is not None and (not isinstance(task_id, str) or not task_id or "/" in task_id or "\\" in task_id or len(task_id) > 128):
            raise ValueError("Invalid context task_id")
        settings = resolve(self.root, task_id)["values"]["context"]
        budget = Budget(settings, request.get("budget", {}))
        selectors, held_rows = request.get("selectors", []), request.get("held", [])
        if not isinstance(selectors, list) or not isinstance(held_rows, list) or len(selectors) + len(held_rows) > settings["max_units"]:
            raise ValueError("Context selector/held limit exceeded")
        held = {}
        for item in held_rows:
            if not isinstance(item, dict) or set(item) != {"unit_id", "unit_revision"} or any(not isinstance(v, str) for v in item.values()):
                raise ValueError("held requires unit_id and unit_revision")
            if item["unit_id"] in held:
                raise ValueError("Duplicate held unit")
            held[item["unit_id"]] = item["unit_revision"]
        mode = request.get("delivery", "full")
        if mode not in {"full", "delta"}:
            raise ValueError("delivery must be full or delta")
        workspace = Workspace(self.root)
        manager = nullcontext(self.index) if self.index else Index(self.root)
        with manager as index, index.read_session():
            session = Selection(self.root, index, settings, task_id, self.resident)
            candidates, missing = [], []
            if task_id:
                from .task_store import load_task
                task = load_task(self.root, task_id)
                activity = task["current_activity"]
                path = f"{CONTROL}/tasks/{task_id}/current.md"
                candidates.append((session.runtime(path), True, "current_task"))
                for dep in task.get("dependencies", []):
                    if dep["consumer"] == task["current_activity"]:
                        if not {"unit_id", "unit_revision"} <= dep.keys():
                            raise ValueError("Obsolete dependency format; explicitly rebind accepted baselines")
                        unit = session.lookup(dep["unit_id"])
                        if not unit or unit["unit_revision"] != dep["unit_revision"]:
                            missing.append({"unit_id": dep["unit_id"], "reason": "stale_upstream"})
                        else:
                            candidates.append((unit, True, "upstream"))
            for selector in selectors:
                try:
                    found = session.select(selector)
                except ReadBudgetExceeded:
                    missing.append({"selector": selector, "reason": "read_budget_exceeded"})
                    continue
                if len(found) != 1:
                    missing.append({"selector": selector, "reason": "ambiguous" if found else "not_found",
                                    "candidates": [u["unit_id"] for u in found[:8]]})
                else:
                    candidates.append((found[0], selector.get("required", False), "explicit"))
            if request.get("query"):
                rows = index.search(request["query"], limit=min(settings["max_candidates"], index.config["max_results"]))
                for row in rows:
                    unit = session.row_unit(row)
                    if unit:
                        candidates.append((unit, False, "query"))
            mandatory, optional, deferred = [], [], []
            for unit, required, reason in candidates:
                group, errors = session.closure(unit)
                if errors:
                    issue = {"unit_id": unit["unit_id"], "reason": "dependency_incomplete", "details": errors[:8]}
                    (missing if required or reason == "explicit" else deferred).append(issue)
                else:
                    (mandatory if required else optional).append((group, reason))
            required = {u["unit_id"] for group, _ in mandatory for u in group}
            value = {"schema_version": 2, "ok": True, "status": "complete", "publication_id": index.read_revision, "task_id": task_id,
                     "delivery": mode, "units": [], "coverage": {"required": len(required), "satisfied": 0,
                     "unresolved": len(missing), "deferred": 0}, "missing": missing[:8], "deferred": [], "body": [], "usage": {}}

            def extend(chosen, group, reason):
                result = {k: (u, set(r)) for k, (u, r) in chosen.items()}
                for unit in group:
                    result.setdefault(unit["unit_id"], (unit, set()))[1].add(reason)
                return result

            def render(chosen):
                result = {**value, "units": [], "body": [], "usage": {}}
                ranges, held_ranges = {}, {}
                if mode == "delta":
                    for held_id, revision in held.items():
                        unit = session.lookup(held_id)
                        if unit and unit["unit_revision"] == revision:
                            held_ranges.setdefault(unit["path"], []).append((unit["start"], unit["end"]))
                for key, (unit, reasons) in chosen.items():
                    possessed = mode == "delta" and held.get(key) == unit["unit_revision"]
                    result["units"].append({**unit, "reasons": sorted(reasons), "delivery": "held" if possessed else "body"})
                    if not possessed:
                        ranges.setdefault(unit["path"], []).append((unit["start"], unit["end"]))
                for path in sorted(ranges):
                    def merge(intervals):
                        merged = []
                        for start, end in sorted(intervals):
                            if merged and start <= merged[-1][1] + 1:
                                merged[-1][1] = max(end, merged[-1][1])
                            else:
                                merged.append([start, end])
                        return merged
                    active, possessed = merge(ranges[path]), merge(held_ranges.get(path, []))
                    for start, end in active:
                        remaining = [(start, end)]
                        for held_start, held_end in possessed:
                            remaining = [(left, min(right, held_start - 1)) for left, right in remaining if left < held_start] + [(max(left, held_end + 1), right) for left, right in remaining if right > held_end]
                        lines = session.read(path)
                        for left, right in remaining:
                            result["body"].append({"path": path, "start": left, "end": right, "text": "\n".join(lines[left - 1:right])})
                return result

            chosen = {}
            for group, reason in mandatory:
                chosen = extend(chosen, group, reason)
            if len(chosen) > settings["max_units"]:
                missing.append({"reason": "unit_limit"})
                value["missing"] = missing[:8]
                value["coverage"]["unresolved"] = len(missing)
            if missing:
                value.update(ok=False, status="needs_selection" if any(m["reason"] == "ambiguous" for m in missing) else "material_missing")
                chosen = {}
            else:
                value["coverage"]["satisfied"] = len(required)
                try:
                    mandatory_result = render(chosen)
                    fits = budget.fits(mandatory_result, session.read_bytes)
                except ReadBudgetExceeded:
                    mandatory_result = {"usage": {"output_bytes": None, "tokens": None}}
                    fits = False
                if not fits:
                    value.update(ok=False, status="insufficient_budget")
                    value["coverage"]["satisfied"] = 0
                    value["missing"] = [{"reason": "required_budget_exceeded", "needed_output_bytes": mandatory_result["usage"]["output_bytes"], "needed_tokens": mandatory_result["usage"]["tokens"]}]
                    chosen = {}
            if value["ok"] and optional:
                # Candidates arrive in deterministic relevance order. Prefix
                # search keeps the best fitting set while limiting full payload
                # serializations from O(n) trials to O(log n).
                low, high = 0, len(optional)
                while low < high:
                    middle = (low + high + 1) // 2
                    trial = chosen
                    for group, reason in optional[:middle]:
                        trial = extend(trial, group, reason)
                    new_paths = {unit["path"] for group, _ in optional[:middle]
                                 for unit in group if unit["path"] not in session.cache}
                    read_cost = session.read_bytes + sum(local(self.root, path).stat().st_size for path in new_paths)
                    try:
                        fits = (len(trial) <= settings["max_units"]
                                and read_cost <= settings["max_read_bytes"]
                                and budget.fits(render(trial), session.read_bytes))
                    except ReadBudgetExceeded:
                        fits = False
                    if fits:
                        low = middle
                    else:
                        high = middle - 1
                for group, reason in optional[:low]:
                    chosen = extend(chosen, group, reason)
                deferred_paths = set(session.cache)
                deferred_read = session.read_bytes
                for group, _ in optional[low:]:
                    paths = {unit["path"] for unit in group} - deferred_paths
                    needed = sum(local(self.root, path).stat().st_size for path in paths)
                    deferred_read += needed
                    deferred_paths.update(paths)
                    reason = "read_budget_exceeded" if deferred_read > settings["max_read_bytes"] else "budget_exceeded"
                    deferred.append({"unit_id": group[0]["unit_id"], "reason": reason})
            value["deferred"], value["coverage"]["deferred"] = deferred[:8], len(deferred)
            result = render(chosen)
            while not budget.fits(result, session.read_bytes):
                if set(chosen) - required:
                    chosen = {k: v for k, v in chosen.items() if k in required}
                    value["coverage"]["deferred"] = len(optional) + len(deferred)
                elif value["deferred"]:
                    value["deferred"] = []
                elif value["missing"] and value["missing"][0].get("reason") != "details_exceed_budget":
                    value["missing"] = [{"reason": "details_exceed_budget", "count": len(missing) or 1}]
                elif chosen:
                    needed = result["usage"]["output_bytes"]
                    chosen = {}
                    value.update(ok=False, status="insufficient_budget")
                    value["coverage"]["satisfied"] = 0
                    value["missing"] = [{"reason": "required_budget_exceeded", "needed_output_bytes": needed}]
                else:
                    raise ValueError("Context budget cannot contain the result envelope")
                result = render(chosen)
            session.verify()
        from .support.trace_metrics import record_context
        record_context(self.root, task_id, activity, result, round((time.monotonic() - started) * 1000, 3))
        return result


class Selection:
    def __init__(self, root, index, settings, task_id, resident=None):
        self.root, self.index, self.settings, self.task_id = root, index, settings, task_id
        self.publication = read_json(root / PUBLICATION)
        self.cache, self.observed, self.runtime_units, self.lookups, self.closures = {}, {}, {}, {}, {}
        self.read_bytes = 0
        self.resident = resident
        if resident:
            resident.refresh()

    def safe_path(self, path):
        if not isinstance(path, str):
            raise ValueError("Context path must be a string")
        path = str(local(self.root, path).relative_to(self.root))
        parts = Path(path).parts
        runtime = bool(parts and parts[0] == CONTROL)
        allowed = self.task_id and parts[:3] == (CONTROL, "tasks", self.task_id) and (
            parts[3:] in {("current.md",), ("plan.md",)} or len(parts) > 4 and parts[3] == "evidence")
        if "history" in parts or runtime and not allowed:
            raise ValueError("Private recovery/runtime data is excluded from model context")
        return path

    def read(self, path):
        path = self.safe_path(path)
        if path not in self.cache:
            file = local(self.root, path)
            size = file.stat().st_size
            if size > self.index.config["max_file_bytes"] or self.read_bytes + size > self.settings["max_read_bytes"]:
                raise ReadBudgetExceeded("Context read budget exceeded")
            pinned = self.resident.items.get(path) if self.resident else None
            if pinned:
                data = pinned["text"].encode()
                if sha(data) != pinned["source_digest"]:
                    raise ValueError("Resident context digest mismatch")
            else:
                with file.open("rb") as stream:
                    data = stream.read(size + 1)
            if len(data) != size:
                raise ValueError("Context source changed during read")
            self.read_bytes += size
            digest = sha(data)
            if not path.startswith(CONTROL + "/") and self.publication["sources"].get(path) != digest:
                raise ValueError("Context source differs from publication")
            text = data.decode("utf-8")
            if text.count("\n") > 200_000:
                raise ReadBudgetExceeded("Source line count exceeds context memory bound")
            self.observed[path] = digest
            self.cache[path] = text.splitlines()
        return self.cache[path]

    def row_unit(self, row):
        props = json.loads(row["properties"]) if isinstance(row["properties"], str) else row["properties"]
        if "unit_id" not in props:
            return None
        return {"unit_id": props["unit_id"], "unit_revision": props["unit_revision"], "path": self.safe_path(row["path"]),
                "start": row["start"], "end": row["end"], "kind": props["unit_kind"], "parent_id": props["parent_id"],
                "completeness": props["completeness"], "source_digest": row["digest"]}

    def lookup(self, key):
        if key in self.runtime_units:
            return self.runtime_units[key]
        if key not in self.lookups:
            import re
            line_unit = re.fullmatch(r"file:(.+)#lines:(\d+)-(\d+)", key)
            if line_unit:
                path, start, end = line_unit.group(1), int(line_unit.group(2)), int(line_unit.group(3))
                path = self.safe_path(path)
                base = self.lookup(file_id(path))
                if base and start >= 1 and end >= start and end <= base["end"]:
                    text = "\n".join(self.read(path)[start - 1:end])
                    self.lookups[key] = {**base, "unit_id": key, "unit_revision": sha(text.encode()),
                                         "start": start, "end": end, "kind": "lines", "parent_id": file_id(path)}
                else:
                    self.lookups[key] = None
            else:
                if key.startswith("file:"):
                    self.safe_path(key[5:])
                row = self.index.connect().execute("SELECT * FROM items WHERE key=?", (key,)).fetchone()
                self.lookups[key] = self.row_unit(row) if row else None
        return self.lookups[key]

    def runtime(self, path):
        lines = self.read(path)
        unit = {"unit_id": file_id(path), "unit_revision": self.observed[path], "path": path,
                "start": 1, "end": len(lines), "kind": "task", "parent_id": None,
                "completeness": "atomic", "source_digest": self.observed[path]}
        self.runtime_units[unit["unit_id"]] = unit
        return unit

    def select(self, selector):
        if not isinstance(selector, dict) or set(selector) - {"unit_id", "path", "scope", "required"} or type(selector.get("required", False)) is not bool:
            raise ValueError("Invalid context selector")
        if "unit_id" in selector:
            if set(selector) - {"unit_id", "required"} or not isinstance(selector["unit_id"], str):
                raise ValueError("Unit selector requires only unit_id and required")
            unit = self.lookup(selector["unit_id"])
            return [unit] if unit else []
        path = self.safe_path(selector.get("path"))
        scope = selector.get("scope")
        shapes = {"file": {"kind"}, "lines": {"kind", "start", "end"}, "symbol": {"kind", "name"}, "section": {"kind", "title"}}
        if not isinstance(scope, dict) or scope.get("kind") not in shapes or set(scope) != shapes[scope["kind"]]:
            raise ValueError("An explicit valid context scope is required")
        kind = scope["kind"]
        if kind == "file":
            unit = self.lookup(file_id(path))
            return [unit] if unit else []
        if kind == "lines":
            start, end = scope["start"], scope["end"]
            if type(start) is not int or type(end) is not int or start < 1 or end < start:
                raise ValueError("Invalid line range")
            base = self.lookup(file_id(path))
            if not base or end > base["end"]:
                return []
            text = "\n".join(self.read(path)[start - 1:end])
            return [{**base, "unit_id": file_id(path) + f"#lines:{start}-{end}", "start": start, "end": end,
                     "kind": "lines", "parent_id": base["unit_id"], "completeness": "atomic", "unit_revision": sha(text.encode())}]
        name = scope.get("name", scope.get("title"))
        if not isinstance(name, str):
            raise ValueError("Scope name must be a string")
        rows = self.index.connect().execute("SELECT * FROM items WHERE path=? AND title=? ORDER BY key LIMIT ?", (path, name, self.settings["max_units"] + 1))
        return [u for row in rows if (u := self.row_unit(row)) and u["kind"] == kind]

    def closure(self, unit):
        if unit["unit_id"] in self.closures:
            return self.closures[unit["unit_id"]]
        result, visited, active, errors = [], set(), set(), []
        def visit(current, depth):
            key = current["unit_id"]
            if key in active:
                errors.append({"unit_id": key, "reason": "dependency_cycle"})
                return
            if key in visited:
                return
            if len(visited) >= self.settings["max_units"] or depth > self.settings["max_dependency_depth"]:
                errors.append({"unit_id": key, "reason": "dependency_limit"})
                return
            visited.add(key)
            active.add(key)
            result.append(current)
            ancestors, seen_parents = [key], set()
            parent = current.get("parent_id")
            while parent and parent not in seen_parents:
                seen_parents.add(parent)
                ancestors.append(parent)
                record = self.lookup(parent)
                parent = record.get("parent_id") if record else None
                if len(ancestors) > self.settings["max_dependency_depth"] + 1:
                    errors.append({"unit_id": key, "reason": "parent_limit"})
                    break
            targets = set()
            if current["kind"] == "file":
                children = self.index.connect().execute(
                    "SELECT DISTINCT r.source AS key FROM relations r JOIN items i ON i.key=r.source "
                    "WHERE i.path=? AND r.source<>? AND r.kind='requires' ORDER BY key LIMIT ?",
                    (current["path"], key, self.settings["max_units"] + 1)).fetchall()
                if len(children) > self.settings["max_units"]:
                    errors.append({"unit_id": key, "reason": "dependency_limit"})
                else:
                    ancestors.extend(r[0] for r in children)
            for source in ancestors:
                targets.update(r[0] for r in self.index.connect().execute(
                    "SELECT target FROM relations WHERE source=? AND kind='requires' ORDER BY target LIMIT ?",
                    (source, self.settings["max_units"] + 1)) if source == key or r[0] != key)
            for target_id in sorted(targets):
                target = self.lookup(target_id)
                if target is None:
                    errors.append({"unit_id": target_id, "reason": "missing_dependency"})
                elif current["kind"] == "file" and target["path"] == current["path"]:
                    continue
                else:
                    visit(target, depth + 1)
            active.remove(key)
        visit(unit, 0)
        self.closures[unit["unit_id"]] = (result, errors)
        return result, errors

    def verify(self):
        for path, digest in self.observed.items():
            if fingerprint(local(self.root, path)) != digest:
                raise ValueError("Context source changed; discard and retry")


def assemble(root, request):
    return ContextProvider(root).obtain(request)
