from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict, Json
from pydantic import ConfigDict


class HatchetServiceSchedulerModel(HomelabBaseModel):
    workflow: str
    schedules: list[str]
    input: Json | None


class HatchetServiceSchedulerConfig(
    HomelabServiceConfigDict[HatchetServiceSchedulerModel]
):
    model_config = ConfigDict(frozen=False)

    NONE_KEY = "scheduler"
