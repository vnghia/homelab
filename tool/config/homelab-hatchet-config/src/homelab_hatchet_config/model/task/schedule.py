import dataclasses

from homelab_pydantic import Json


@dataclasses.dataclass
class HatchetTaskWorkflowInputArgs:
    workflow: str
    input: Json | None


@dataclasses.dataclass
class HatchetTaskScheduleArgs:
    workflow: str
    schedules: list[str]
    input: Json | None
