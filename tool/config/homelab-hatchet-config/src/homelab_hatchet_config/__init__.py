from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict, Json
from pydantic import ConfigDict

from .model.docker import HatchetServiceDockerConfig
from .model.scheduler import HatchetServiceSchedulerConfig
from .model.task import HatchetTaskModel


class HatchetTaskConfig(HomelabServiceConfigDict[HatchetTaskModel]):
    NONE_KEY = "task"


class HatchetServiceConfigModel(HomelabServiceConfigDict[Json]):
    model_config = ConfigDict(frozen=False)

    NONE_KEY = "config"


class HatchetServiceConfig(HomelabBaseModel):
    docker: HatchetServiceDockerConfig = HatchetServiceDockerConfig()
    task: HatchetTaskConfig = HatchetTaskConfig({})
    config: HatchetServiceConfigModel = HatchetServiceConfigModel({})
    scheduler: HatchetServiceSchedulerConfig = HatchetServiceSchedulerConfig({})

    def __bool__(self) -> bool:
        return (
            bool(self.docker)
            or bool(self.task)
            or bool(self.config)
            or bool(self.scheduler)
        )


class HatchetServiceConfigBase(HomelabBaseModel):
    hatchet: HatchetServiceConfig = HatchetServiceConfig()
