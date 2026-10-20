"""Validate published activity assets and package version without executing downloads."""

import json
import re
from pathlib import Path
from . import __version__

LINK = re.compile(r"\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)")


def validate(root):
    root = Path(root).resolve()
    errors = []
    references = root / "references"
    scripts = root / "scripts"
    if not references.is_dir():
        references = root / "hs-dev-skill/share"
    if not scripts.is_dir():
        scripts = root / "hs-dev-skill/scripts"
    docs = references / "skill-docs"
    if not docs.is_dir():
        docs = root / "hs-dev-docs"
    skill_file = root / "SKILL.md"
    if not skill_file.is_file():
        skill_file = root / "hs-dev-skill/SKILL.md"
    required = [str(skill_file.relative_to(root)), "README.md", str(scripts.relative_to(root) / "pyproject.toml"),
                str(scripts.relative_to(root) / "hs_dev/data/workflow.json"),
                str(scripts.relative_to(root) / "hs_dev/cli.py")]
    for name in required:
        if not (root / name).is_file():
            errors.append("Missing bundle file: " + name)
    if errors:
        return {"ok": False, "errors": errors}
    data = json.loads((scripts / "hs_dev/data/workflow.json").read_text())
    if data["version"] != __version__:
        errors.append("Catalog version mismatch")
    if f'version = "{__version__}"' not in (scripts / "pyproject.toml").read_text():
        errors.append("Project version mismatch")
    if f'version: "{__version__}"' not in skill_file.read_text():
        errors.append("Skill version mismatch")
    seen = set()
    for stage in data["stages"]:
        if not (root / stage["path"] / "stage-overview.md").exists():
            errors.append("Stage overview missing: " + stage["id"])
        for activity in stage["activities"]:
            base = root / activity["path"]
            for name in ("activity-guide.md", "checklist.md"):
                if not (base / name).is_file():
                    errors.append("Activity asset missing: " + str(base / name))
            for check in activity["checks"]:
                if check["id"] in seen or not check["criterion"] or not check["method"]:
                    errors.append("Invalid/duplicate internal check: " + check["id"])
                seen.add(check["id"])
                if (base / "checklist.md").exists() and check["criterion"] not in (base / "checklist.md").read_text():
                    errors.append("Checklist/catalog drift: " + check["id"])
    for folder in (references, docs):
        if not folder.exists():
            continue
        for file in [*folder.rglob("*.md"), *folder.rglob("*.idx")]:
            for target in LINK.findall(file.read_text(encoding="utf-8")):
                if "://" in target or target.startswith(("#", "mailto:")):
                    continue
                resolved = file.parent / target.split("#", 1)[0]
                if not resolved.exists():
                    errors.append("Broken link: " + str(file.relative_to(root)) + " -> " + target)
    return {"ok": not errors, "version": __version__, "internal_checks": len(seen), "errors": errors}
