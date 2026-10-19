"""Explicit current-package installation. Never touches project data or migrates formats."""

import shutil
import tempfile
from pathlib import Path


def install(source, target):
    source, target = Path(source).resolve(), Path(target).absolute()
    if target.is_symlink() or (target / ".git").exists() or source == target or source in target.parents or target in source.parents:
        raise ValueError("Installation must be separate from source and versioned workspaces")
    from ..bundle import validate
    result = validate(source)
    if not result["ok"]:
        raise ValueError("Invalid source bundle: " + str(result["errors"]))
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="hs-update-", dir=target.parent) as temporary:
        stage, backup = Path(temporary) / "stage", Path(temporary) / "backup"
        shutil.copytree(source, stage, ignore=shutil.ignore_patterns(".git", "__pycache__", "*.egg-info", "hs_dev_docs", ".pytest_cache", "dist", "build"))
        if not validate(stage)["ok"]:
            raise ValueError("Staged package validation failed")
        existed = target.exists()
        if existed:
            target.rename(backup)
        try:
            stage.rename(target)
            if not validate(target)["ok"]:
                raise ValueError("Installed package validation failed")
        except Exception:
            if target.exists():
                shutil.rmtree(target)
            if existed:
                backup.rename(target)
            raise
    return {"ok": True, "target": str(target)}
