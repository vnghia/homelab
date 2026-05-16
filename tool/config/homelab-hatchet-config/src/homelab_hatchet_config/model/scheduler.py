from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict
from pydantic import ConfigDict


class HatchetServiceSchedulerModel(HomelabBaseModel):
    workflow: str
    schedules: list[str]
    input: Any | None


class HatchetServiceSchedulerConfig(
    HomelabServiceConfigDict[HatchetServiceSchedulerModel]
):
    model_config = ConfigDict(frozen=False)

    NONE_KEY = "scheduler"
