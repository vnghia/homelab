import dataclasses
from pathlib import PosixPath
from typing import Self

import pulumi_docker as docker
from pulumi import Input, Output
from pydantic import BaseModel

from homelab_docker.model.container.volume import ContainerVolumesConfig
from homelab_docker.pydantic.path import RelativePath
from homelab_docker.resource.volume import VolumeResource


@dataclasses.dataclass
class ContainerVolumeResourcePath:
    name: str
    volume: docker.Volume
    path: RelativePath

    def to_props(self) -> dict[str, Input[str]]:
        return {
            "volume": self.volume.name,
            "path": Output.from_input(self.path).apply(PosixPath.as_posix),
        }


class ContainerVolumePath(BaseModel):
    volume: str
    path: RelativePath = PosixPath("")

    def to_container_path(
        self, container_volumes_config: ContainerVolumesConfig
    ) -> PosixPath:
        path = container_volumes_config[self.volume].to_container_path()
        return path / self.path if self.path else path

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())

    def to_resource(
        self, volume_resource: VolumeResource
    ) -> ContainerVolumeResourcePath:
        return ContainerVolumeResourcePath(
            name=self.volume, volume=volume_resource[self.volume], path=self.path
        )

    def join(self, path: RelativePath, suffix: str) -> Self:
        return self.model_copy(update={"path": (self.path / path).with_suffix(suffix)})
