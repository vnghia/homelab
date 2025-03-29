from pathlib import PosixPath
from typing import ClassVar

from homelab_docker.extract import GlobalExtract
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.volume import LocalVolumeModel
from homelab_pydantic import AbsolutePath, HomelabBaseModel, RelativePath


class ResticVolumeConfig(HomelabBaseModel):
    MOUNT_PATH: ClassVar[AbsolutePath] = AbsolutePath(PosixPath("/mnt"))

    name: str
    model: LocalVolumeModel
    relative: RelativePath | None = None

    @property
    def service(self) -> str:
        return self.name.split("-", maxsplit=1)[0]

    @property
    def path(self) -> AbsolutePath:
        if self.relative:
            return self.MOUNT_PATH / self.relative
        else:
            return self.MOUNT_PATH / self.service / self.name

    @property
    def container_volume_config(self) -> ContainerVolumeConfig:
        return ContainerVolumeConfig(GlobalExtract.from_simple(self.path.as_posix()))
