"""Field-wise configuration resolution with provenance and validated bounds."""

import json
from pathlib import Path
from .storage import CONTROL, local, read_json, now

MODES = {"mute", "stage", "activity"}
MEMORY_LIMIT = 200_000_000
DEFAULTS = {
    "execution": {"mode": "stage"},
    "index": {"memory_bytes": MEMORY_LIMIT, "lru_bytes": 48_000_000, "resident_bytes": 16_000_000,
              "sqlite_cache_kib": 24_000, "max_file_bytes": 2_000_000, "max_results": 100},
    "retention": {"hours": 48, "tasks": 5, "snapshots": 5},
    "trace": {"enabled": False},
}


def resolve(root, task_id=None, direct=None, home=None):
    if task_id is None:
        active = [p.parent.name for p in (Path(root) / CONTROL / "task").glob("*/task.json")
                  if read_json(p).get("status") == "ACTIVE"]
        if len(active) == 1:
            task_id = active[0]
    values = json.loads(json.dumps(DEFAULTS))
    sources = {}
    locations = [(Path(home or Path.home()) / ".hs-dev-skill/config/config.json", "host"),
                 (Path(root) / CONTROL / "config/config.json", "project")]
    if task_id:
        locations.append((local(root, f"{CONTROL}/task/{task_id}/config/config.json"), "task"))

    def merge(data, label):
        if not isinstance(data, dict):
            raise ValueError("Configuration must be an object")
        for section, fields in data.items():
            if section not in DEFAULTS or not isinstance(fields, dict):
                raise ValueError("Unknown configuration section: " + section)
            for key, value in fields.items():
                if key not in DEFAULTS[section] or type(value) is not type(DEFAULTS[section][key]):
                    raise ValueError("Unknown or mistyped configuration: " + section + "." + key)
                values[section][key] = value
                sources[section + "." + key] = label

    for path, label in locations:
        if path.exists():
            merge(json.loads(path.read_text(encoding="utf-8")), label)
    merge(direct or {}, "direct")
    if values["execution"]["mode"] not in MODES:
        raise ValueError("execution.mode must be mute, stage or activity")
    for section in ("index", "retention"):
        if any(value <= 0 for value in values[section].values()):
            raise ValueError("Numeric budgets must be positive")
    budget = values["index"]
    if budget["memory_bytes"] > MEMORY_LIMIT:
        raise ValueError("Index process memory cannot exceed 200 MB")
    reserved = budget["lru_bytes"] + budget["resident_bytes"] + budget["sqlite_cache_kib"] * 1024
    if reserved > budget["memory_bytes"] // 2:
        raise ValueError("Leave at least half the process budget for runtime and bounded query work")
    if values["retention"]["hours"] > 48 or values["retention"]["tasks"] > 5 or values["retention"]["snapshots"] > 5:
        raise ValueError("Retention may be tightened, not extended beyond 48 hours / 5 entries")
    return {"values": values, "sources": sources, "task_id": task_id, "resolved_at": now()}


ENVIRONMENTS = {"dev", "dev.mock", "test", "test.mock", "sandbox", "online"}


def environment(root, name, injected=None):
    if name not in ENVIRONMENTS:
        raise ValueError("Environment must be explicitly selected")
    config = Path(root) / "config"
    files = [config / "env.defaults", config / ("env." + name.split(".")[0])]
    if name.endswith(".mock"):
        files.append(config / ("env." + name))
    result = {}
    for file in files:
        if not file.exists():
            raise ValueError("Missing environment file: " + str(file))
        for line in file.read_text(encoding="utf-8").splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, separator, value = line.partition("=")
                if not separator or not key.strip():
                    raise ValueError("Malformed environment assignment")
                result[key.strip()] = value.strip()
    result.update(injected or {})
    if result.get("USE_MOCK", "false") not in {"true", "false"}:
        raise ValueError("USE_MOCK must be true or false")
    if name in {"sandbox", "online"} and result.get("USE_MOCK") == "true":
        raise ValueError("Mock cannot be enabled in sandbox or online")
    return result
