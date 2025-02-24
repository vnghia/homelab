from __future__ import annotations

import typing

from homelab_dagu_service.config.group.docker import DaguDagDockerGroupConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service.extract import ServiceExtract
from homelab_pydantic import HomelabBaseModel

from .keep import ResticKeepConfig
from .repo import ResticRepoConfig

if typing.TYPE_CHECKING:
    from .. import ResticService


class ResticConfig(HomelabBaseModel):
    image: str
    profile_dir: ServiceExtract
    cache_dir: ServiceExtract

    repo: ResticRepoConfig
    keep: ResticKeepConfig

    dagu: DaguDagDockerGroupConfig

    def get_profile_volume_path(
        self, restic_service: ResticService, name: str
    ) -> ContainerVolumePath:
        return self.profile_dir.extract_volume_path(restic_service.model) / name
