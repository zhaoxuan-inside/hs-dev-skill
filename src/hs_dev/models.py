"""Named check records; rule text is resolved from one catalog, never copied."""

from dataclasses import asdict, dataclass
from typing import TypedDict, NotRequired


class DependencyBinding(TypedDict):
    consumer: str
    producer: str
    path: str
    digest: str
    actor: str
    confirmation: str
    bound_at: str


class ApprovalRecord(TypedDict):
    actor: str
    confirmation: str
    confirmed_at: str
    checklist_digest: str
    material_digest: str
    dependency_digest: str


class TaskRecord(TypedDict):
    schema_version: int
    task_id: str
    title: str
    status: str
    mode: str
    activities: list[str]
    current_activity: str
    approvals: dict[str, ApprovalRecord]
    dependencies: NotRequired[list[DependencyBinding]]
    outputs: NotRequired[dict[str, list[str]]]
    created_at: str
    updated_at: str
    snapshot_id: NotRequired[str]
    verification: str | None


@dataclass
class CheckExecution:
    check_id: str
    rule_digest: str
    result: str = "PENDING"
    evidence: str = ""
    evidence_digest: str = ""
    reason: str = ""

    def to_dict(self):
        return asdict(self)
