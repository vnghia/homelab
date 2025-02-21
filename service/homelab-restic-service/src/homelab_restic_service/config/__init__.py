from homelab_dagu_service.config.group.docker import DaguDagDockerGroupConfig
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_pydantic import HomelabBaseModel

from .keep import ResticKeepConfig
from .repo import ResticRepoConfig


class ResticConfig(HomelabBaseModel):
    image: str
    profile_dir: ContainerVolumePath

    repo: ResticRepoConfig
    keep: ResticKeepConfig

    dagu: DaguDagDockerGroupConfig

    def get_profile_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.profile_dir / file
