from __future__ import annotations

from homelab_dagu_config import DaguServiceConfigBase
from homelab_docker.extract.service import ServiceExtract

from .keep import ResticKeepConfig
from .repo import ResticRepoConfig


class ResticConfig(DaguServiceConfigBase):
    image: str
    profile_dir: ServiceExtract
    cache_dir: ServiceExtract

    repo: ResticRepoConfig
    password: ServiceExtract
    keep: ResticKeepConfig
