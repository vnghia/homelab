from __future__ import annotations

from homelab_dagu_config.group.docker import DaguDagDockerGroupConfig
from homelab_dagu_config.model.dotenv import DaguDotenvModel
from homelab_docker.extract.service import ServiceExtract
from homelab_pydantic import HomelabBaseModel

from .keep import ResticKeepConfig
from .repo import ResticRepoConfig


class ResticConfig(HomelabBaseModel):
    image: str
    profile_dir: ServiceExtract
    cache_dir: ServiceExtract

    repo: ResticRepoConfig
    password: ServiceExtract
    keep: ResticKeepConfig

    dagu: DaguDagDockerGroupConfig
    dotenv: DaguDotenvModel
