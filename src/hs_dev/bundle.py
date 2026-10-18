"""Validate published activity assets and package version without executing downloads."""

import json
import re
from pathlib import Path
from . import __version__

LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def validate(root):
    root = Path(root).resolve()
    errors = []
    required = ["SKILL.md", "README.md", "pyproject.toml", "src/hs_dev/data/workflow.json", "src/hs_dev/cli.py"]
    for name in required:
        if not (root / name).is_file():
            errors.append("Missing bundle file: " + name)
    if errors:
        return {"ok": False, "errors": errors}
    data = json.loads((root / "src/hs_dev/data/workflow.json").read_text())
    if data["version"] != __version__:
        errors.append("Catalog version mismatch")
    if f'version = "{__version__}"' not in (root / "pyproject.toml").read_text():
        errors.append("Project version mismatch")
    if f'version: "{__version__}"' not in (root / "SKILL.md").read_text():
        errors.append("Skill version mismatch")
    seen = set()
    for stage in data["stages"]:
        if not (root / stage["path"] / "README.md").exists():
            errors.append("Stage README missing: " + stage["id"])
        for activity in stage["activities"]:
            base = root / activity["path"]
            for name in ("README.md", "checklist.md", "guide.md", "activity.json"):
                if not (base / name).is_file():
                    errors.append("Activity asset missing: " + str(base / name))
            for check in activity["checks"]:
                if check["id"] in seen or not check["criterion"] or not check["method"]:
                    errors.append("Invalid/duplicate internal check: " + check["id"])
                seen.add(check["id"])
                if (base / "checklist.md").exists() and check["criterion"] not in (base / "checklist.md").read_text():
                    errors.append("Checklist/catalog drift: " + check["id"])
            if (base / "activity.json").exists() and json.loads((base / "activity.json").read_text()) != activity:
                errors.append("Activity catalog drift: " + activity["id"])
    for folder in ("workflow", "skills", "references", "catalogs"):
        for file in (root / folder).rglob("*.md"):
            for target in LINK.findall(file.read_text(encoding="utf-8")):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                resolved = file.parent / target.split("#", 1)[0]
                if not resolved.exists():
                    errors.append("Broken link: " + str(file.relative_to(root)) + " -> " + target)
    return {"ok": not errors, "version": __version__, "internal_checks": len(seen), "errors": errors}
