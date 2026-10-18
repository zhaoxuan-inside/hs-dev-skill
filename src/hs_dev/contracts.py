"""Named domain states shared by configuration, workflow and recovery."""

from enum import StrEnum


class TaskStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"


class OperationState(StrEnum):
    PREPARED = "PREPARED"
    VERIFIED = "VERIFIED"
    INTERRUPTED = "INTERRUPTED"
    COMMITTED = "COMMITTED"
    ROLLED_BACK = "ROLLED_BACK"


class CheckResult(StrEnum):
    PENDING = "PENDING"
    PASS = "PASS"
    FAIL = "FAIL"
    NA = "NA"


class ExecutionMode(StrEnum):
    MUTE = "mute"
    STAGE = "stage"
    ACTIVITY = "activity"
