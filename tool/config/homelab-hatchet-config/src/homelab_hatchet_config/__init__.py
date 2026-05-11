from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from .model.docker import HatchetServiceDockerConfig
from .model.task import HatchetTaskModel


class HatchetTaskConfig(HomelabServiceConfigDict[HatchetTaskModel]):
    NONE_KEY = "task"


class HatchetServiceConfig(HomelabBaseModel):
    docker: HatchetServiceDockerConfig = HatchetServiceDockerConfig()
    task: HatchetTaskConfig = HatchetTaskConfig({})

    def __bool__(self) -> bool:
        return bool(self.docker) or bool(self.task)


class HatchetServiceConfigBase(HomelabBaseModel):
    hatchet: HatchetServiceConfig = HatchetServiceConfig()
