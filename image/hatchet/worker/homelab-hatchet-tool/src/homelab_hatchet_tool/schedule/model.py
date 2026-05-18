from homelab_pydantic import HomelabBaseModel, Json
from homelab_pydantic.model import HomelabServiceConfigDict


class ScheduleModel(HomelabBaseModel):
    workflow: str
    schedules: list[str]
    input: Json | None = None


class ScheduleConfig(HomelabServiceConfigDict[ScheduleModel]):
    NONE_KEY = "schedule"
