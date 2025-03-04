from homelab_pydantic import HomelabBaseModel

from .group.docker import DaguDagDockerGroupConfig
from .model.dotenv import DaguDotenvModel


class DaguServiceConfig(HomelabBaseModel):
    dotenvs: list[DaguDotenvModel] = []
    docker: DaguDagDockerGroupConfig | None = None
