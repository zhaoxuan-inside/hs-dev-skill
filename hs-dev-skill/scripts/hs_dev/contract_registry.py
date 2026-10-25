"""Machine contract registry. Authoritative contracts are machine-readable files; Markdown derives.

E1/E2 contract work registers each contract with its machine file (JSON Schema or
OpenAPI). Structural validation keeps authority machine-checkable, and docs that
claim derivation through `relations` metadata must target registered current
contracts — Markdown never fakes authority it does not have.
"""

import json
from pathlib import Path

from .storage import local, read_json

REGISTRY = "hs_dev_docs/foundation/contracts.json"
SCHEMA_VERSION = 1
KINDS = {"data", "interface"}
FORMATS = {"json-schema", "openapi"}
ROW_FIELDS = {"id", "kind", "format", "path", "status", "version", "notes"}


def load(root):
    return read_json(Path(root) / REGISTRY)


def _structure_problems(doc, label):
    if not isinstance(doc, dict):
        return [label + " is not a JSON object"]
    if "openapi" in doc:
        if not isinstance(doc.get("openapi"), str) or not isinstance(doc.get("paths"), dict) \
                or not isinstance(doc.get("info"), dict) or not isinstance(doc.get("info", {}).get("title"), str):
            return [label + " is not a valid OpenAPI document (openapi/paths/info.title required)"]
        return []
    if isinstance(doc.get("$schema"), str):
        return []
    if isinstance(doc.get("type"), str) and ("properties" in doc or "items" in doc):
        return []
    return [label + " is not a recognizable JSON Schema ($schema or type with properties/items required)"]


def reconcile(root):
    """Registry integrity, machine-file parseability and derive-binding checks."""
    registry = load(root)
    if registry is None:
        return None
    root = Path(root).resolve()
    errors = []
    if not isinstance(registry, dict) or registry.get("schema_version") != SCHEMA_VERSION:
        return {"ok": False, "errors": ["Unsupported contract registry format"], "counts": {}}
    if set(registry) - {"schema_version", "contracts"}:
        errors.append("Unknown contract registry fields")
    rows = registry.get("contracts")
    if not isinstance(rows, list):
        rows = []
        errors.append("Missing contract registry section: contracts")
    seen, current = set(), set()
    for row in rows:
        if not isinstance(row, dict):
            errors.append("Invalid contract row")
            continue
        unknown = set(row) - ROW_FIELDS
        if unknown:
            errors.append("Unknown contract fields " + ",".join(sorted(unknown)) + ": " + str(row.get("id")))
        cid = row.get("id")
        if not isinstance(cid, str) or not cid.strip():
            errors.append("Contract missing id")
            continue
        if cid in seen:
            errors.append("Duplicate contract id: " + cid)
        seen.add(cid)
        if not isinstance(row.get("kind"), str) or row["kind"] not in KINDS:
            errors.append("Unknown contract kind: " + cid)
        fmt = row.get("format")
        if not isinstance(fmt, str) or fmt not in FORMATS:
            errors.append("Unknown contract format: " + cid)
            continue
        if row.get("status", "current") not in {"current", "superseded"}:
            errors.append("Unknown contract status: " + cid)
        path = row.get("path")
        if not isinstance(path, str) or not path.strip():
            errors.append("Contract missing path: " + cid)
            continue
        try:
            file = local(root, path)
        except ValueError:
            errors.append("Invalid contract path: " + cid)
            continue
        if not file.is_file():
            errors.append("Contract file missing: " + cid)
            continue
        if row.get("status", "current") != "current":
            continue
        current.add(cid)
        try:
            doc = json.loads(file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as error:
            errors.append("Contract file is not valid JSON: " + cid + " (" + str(error) + ")")
            continue
        errors.extend(_structure_problems(doc, "Contract " + cid))
    derives = []
    if rows:
        try:
            from .indexing.engine import Index
            with Index(root) as index:
                derives = [dict(row) for row in index.connect().execute(
                    "SELECT DISTINCT target, path FROM relations WHERE kind='derives' ORDER BY target, path")]
        except (ValueError, OSError):
            derives = []
    for row in derives:
        if row["target"] not in current:
            errors.append("Document derives from unknown or superseded contract: " + row["target"]
                          + " (" + row["path"] + ")")
    return {"ok": not errors, "errors": errors,
            "counts": {"contracts": len(rows), "current": len(current), "deriving_docs": len(derives)}}


def report(root):
    result = reconcile(root)
    if result is None:
        return {"ok": True, "registry": False, "errors": [], "counts": {}}
    result["registry"] = True
    return result


def require_consistent(root):
    """E1/E2/E9 gate: a present registry must reconcile clean."""
    result = reconcile(root)
    if result is not None and not result["ok"]:
        raise ValueError("Contract reconciliation failed: " + "; ".join(result["errors"][:8]))
