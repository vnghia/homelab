from pathlib import PosixPath

from homelab_docker.extract import GlobalExtract
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.volume import LocalVolumeModel
from homelab_pydantic import AbsolutePath, HomelabBaseModel


class ResticVolumeConfig(HomelabBaseModel):
    name: str
    model: LocalVolumeModel

    @property
    def service(self) -> str:
        return self.name.split("-", maxsplit=1)[0]

    @property
    def path(self) -> AbsolutePath:
        return AbsolutePath(PosixPath("/mnt")) / self.service / self.name

    @property
    def container_volume_config(self) -> ContainerVolumeConfig:
        return ContainerVolumeConfig(GlobalExtract.from_simple(self.path.as_posix()))
