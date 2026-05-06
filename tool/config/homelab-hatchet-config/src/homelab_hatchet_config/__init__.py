from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from .model.task import HatchetTaskModel


class HatchetTaskConfig(HomelabServiceConfigDict[HatchetTaskModel]):
    NONE_KEY = "task"


class HatchetServiceConfig(HomelabBaseModel):
    task: HatchetTaskConfig = HatchetTaskConfig({})


class HatchetServiceConfigBase(HomelabBaseModel):
    hatchet: HatchetServiceConfig = HatchetServiceConfig()
