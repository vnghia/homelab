from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict

from homelab_dagu_config.model import DaguDagModel

from .group.docker import DaguDagDockerGroupConfig
from .model.dotenv import DaguDagDotenvModel


class DaguDagDotenvConfig(HomelabServiceConfigDict[DaguDagDotenvModel]):
    NONE_KEY = "dotenv"


class DaguDagsConfig(HomelabServiceConfigDict[DaguDagModel]):
    NONE_KEY = "dag"


class DaguServiceConfig(HomelabBaseModel):
    depends_on: list[str] = []
    dotenvs: DaguDagDotenvConfig = DaguDagDotenvConfig({})
    docker: DaguDagDockerGroupConfig | None = None
    dag: DaguDagsConfig = DaguDagsConfig({})

    def __bool__(self) -> bool:
        return bool(self.dotenvs) or bool(self.docker) or bool(self.dag)


class DaguServiceConfigBase(HomelabBaseModel):
    dagu: DaguServiceConfig = DaguServiceConfig()
