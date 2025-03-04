from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from .group.docker import DaguDagDockerGroupConfig
from .model.dotenv import DaguDagDotenvModel


class DaguDagDotenvConfig(HomelabServiceConfigDict[DaguDagDotenvModel]):
    NONE_KEY = "dotenv"


class DaguServiceConfig(HomelabBaseModel):
    dotenvs: DaguDagDotenvConfig = DaguDagDotenvConfig({})
    docker: DaguDagDockerGroupConfig | None = None

    def __bool__(self) -> bool:
        return bool(self.dotenvs) or bool(self.docker)


class DaguServiceConfigBase(HomelabBaseModel):
    dagu: DaguServiceConfig = DaguServiceConfig()
