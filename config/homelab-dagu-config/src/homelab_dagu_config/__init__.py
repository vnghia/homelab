from homelab_pydantic import HomelabBaseModel

from .group.docker import DaguDagDockerGroupConfig
from .model.dotenv import DaguDagDotenvModel


class DaguServiceConfig(HomelabBaseModel):
    dotenvs: list[DaguDagDotenvModel] = []
    docker: DaguDagDockerGroupConfig | None = None


class DaguServiceConfigBase(HomelabBaseModel):
    dagu: DaguServiceConfig | None = None
