from hatchet_sdk.utils.typing import JSONSerializableMapping
from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabServiceConfigDict


class ScheduleModel(HomelabBaseModel):
    workflow: str
    schedules: list[str]
    input: JSONSerializableMapping | None


class ScheduleConfig(HomelabServiceConfigDict[ScheduleModel]):
    NONE_KEY = "schedule"
