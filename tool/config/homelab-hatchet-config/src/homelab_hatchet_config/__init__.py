from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict, Json
from pydantic import ConfigDict

from .model.docker import HatchetServiceDockerConfig
from .model.task import HatchetTaskModel


class HatchetTaskConfig(HomelabServiceConfigDict[HatchetTaskModel]):
    NONE_KEY = "task"


class HatchetServiceConfig(HomelabBaseModel):
    model_config = ConfigDict(frozen=False)

    docker: HatchetServiceDockerConfig = HatchetServiceDockerConfig()
    task: HatchetTaskConfig = HatchetTaskConfig({})
    config: Json = {}

    def __bool__(self) -> bool:
        return bool(self.docker) or bool(self.task)


class HatchetServiceConfigBase(HomelabBaseModel):
    hatchet: HatchetServiceConfig = HatchetServiceConfig()
