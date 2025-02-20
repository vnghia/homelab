from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_pydantic import HomelabBaseModel

from .keep import ResticKeepConfig
from .repo import ResticRepoConfig


class ResticConfig(HomelabBaseModel):
    image: str
    profile_dir: ContainerVolumePath
    repo: ResticRepoConfig
    keep: ResticKeepConfig

    def get_profile_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.profile_dir / file
