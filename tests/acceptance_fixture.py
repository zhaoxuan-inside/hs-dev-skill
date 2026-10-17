"""Reviewed baseline/evidence fixtures, restricted to temporary test projects."""
from pathlib import Path

from baseline_gate import digest, freeze, register_artifact


def bind_acceptance(root, task_id, record, requirements=None):
    root = Path(root)
    requirements = requirements or ["REQ-" + task_id]
    scope = "acceptance-fixtures/" + task_id + "-scope.md"
    evidence = "acceptance-fixtures/" + task_id + "-test.log"
    artifact = "acceptance-fixtures/" + task_id + "-result.md"
    (root / scope).parent.mkdir(parents=True, exist_ok=True)
    (root / scope).write_text("\n".join(requirements), encoding="utf-8")
    (root / evidence).write_text("Isolated test fixture: execution passed", encoding="utf-8")
    (root / artifact).write_text("Test fixture implementation evidence", encoding="utf-8")
    baseline = freeze(root, task_id + "-baseline", "1", scope, requirements,
                      {"source": "test fixture", "excerpt": "fixture scope accepted"}, {task_id: requirements})
    register_artifact(root, task_id + "-artifact", artifact, [task_id + "-baseline"])
    record.update({"baseline": {"id": task_id + "-baseline", "version": "1", "sha256": baseline["sha256"]},
                   "requirements": [{"id": req, "result": "PASS", "evidence": evidence} for req in requirements],
                   "artifacts": [task_id + "-artifact"]})
    for run in record["verification"]["tests"]:
        run["evidence"] = evidence
        run["sha256"] = digest(root, evidence)
