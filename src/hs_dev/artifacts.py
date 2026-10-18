"""Read managed evidence even after current-version task retention relocates it."""

from pathlib import Path
from .storage import CONTROL, local


def evidence_path(root, relative):
    original = local(root, relative)
    if original.is_file():
        return original
    parts = Path(relative).parts
    if len(parts) > 3 and parts[:2] == (CONTROL, "task"):
        archived = local(root, str(Path(CONTROL) / "evidence_archive" / Path(*parts[2:])))
        if archived.is_file():
            return archived
    return original
