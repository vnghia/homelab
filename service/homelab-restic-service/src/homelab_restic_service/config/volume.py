from pathlib import PosixPath
from typing import ClassVar

from homelab_docker.model.docker.container.volume import ContainerVolumeConfig
from homelab_docker.model.docker.volume import LocalVolumeModel
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath, HomelabBaseModel, RelativePath


class ResticVolumeConfig(HomelabBaseModel):
    MOUNT_PATH: ClassVar[AbsolutePath] = AbsolutePath(PosixPath("/mnt"))

    repository: str
    name: str
    service: str
    model: LocalVolumeModel
    relative: RelativePath | None = None

    @property
    def path(self) -> AbsolutePath:
        if self.relative:
            return self.MOUNT_PATH / self.relative
        return self.MOUNT_PATH / self.service / self.name

    @property
    def container_volume_config(self) -> ContainerVolumeConfig:
        return ContainerVolumeConfig(GlobalExtract.from_simple(self.path.as_posix()))
