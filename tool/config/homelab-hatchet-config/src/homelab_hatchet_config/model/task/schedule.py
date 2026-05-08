import dataclasses

from hatchet_sdk.utils.typing import JSONSerializableMapping


@dataclasses.dataclass
class HatchetTaskWorkflowInputArgs:
    workflow: str
    input: JSONSerializableMapping | None


@dataclasses.dataclass
class HatchetTaskScheduleArgs:
    workflow: str
    schedules: list[str]
    input: JSONSerializableMapping | None
