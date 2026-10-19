"""Validate published activity assets and package version without executing downloads."""

import json
import re
from pathlib import Path
from . import __version__

LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def validate(root):
    root = Path(root).resolve()
    errors = []
    required = ["SKILL.md", "README.md", "hs-dev-skill/scripts/pyproject.toml", "hs-dev-skill/scripts/hs_dev/data/workflow.json", "hs-dev-skill/scripts/hs_dev/cli.py"]
    for name in required:
        if not (root / name).is_file():
            errors.append("Missing bundle file: " + name)
    if errors:
        return {"ok": False, "errors": errors}
    data = json.loads((root / "hs-dev-skill/scripts/hs_dev/data/workflow.json").read_text())
    if data["version"] != __version__:
        errors.append("Catalog version mismatch")
    if f'version = "{__version__}"' not in (root / "hs-dev-skill/scripts/pyproject.toml").read_text():
        errors.append("Project version mismatch")
    if f'version: "{__version__}"' not in (root / "SKILL.md").read_text():
        errors.append("Skill version mismatch")
    seen = set()
    for stage in data["stages"]:
        if not (root / stage["path"] / "README.md").exists():
            errors.append("Stage README missing: " + stage["id"])
        for activity in stage["activities"]:
            base = root / activity["path"]
            for name in ("README.md", "checklist.md"):
                if not (base / name).is_file():
                    errors.append("Activity asset missing: " + str(base / name))
            for check in activity["checks"]:
                if check["id"] in seen or not check["criterion"] or not check["method"]:
                    errors.append("Invalid/duplicate internal check: " + check["id"])
                seen.add(check["id"])
                if (base / "checklist.md").exists() and check["criterion"] not in (base / "checklist.md").read_text():
                    errors.append("Checklist/catalog drift: " + check["id"])
    for folder in ("hs-dev-skill/references", "hs-dev-doc"):
        for file in (root / folder).rglob("*.md"):
            for target in LINK.findall(file.read_text(encoding="utf-8")):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                resolved = file.parent / target.split("#", 1)[0]
                if not resolved.exists():
                    errors.append("Broken link: " + str(file.relative_to(root)) + " -> " + target)
    return {"ok": not errors, "version": __version__, "internal_checks": len(seen), "errors": errors}
