"""Explicit JSON value/file input boundary."""
import json
from pathlib import Path

def json_value(value):
    if value is None:
        return None
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)
