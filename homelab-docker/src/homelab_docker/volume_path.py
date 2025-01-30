import dataclasses
from pathlib import PosixPath

import pulumi_docker as docker
from pulumi import Input, Output
from pydantic import BaseModel, ConfigDict

from homelab_docker.container.volume import Volume
from homelab_docker.pydantic.path import RelativePath
from homelab_docker.resource import Resource


@dataclasses.dataclass
class VolumePathInput:
    volume: docker.Volume
    path: Input[RelativePath]

    def to_props(self) -> dict[str, Input[str]]:
        return {
            "volume": self.volume.name,
            "path": Output.from_input(self.path).apply(lambda x: x.as_posix()),
        }


class VolumePath(BaseModel):
    model_config = ConfigDict(strict=True)

    volume: str
    path: RelativePath = PosixPath("")

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())

    def to_str(self, volumes: dict[str, Volume]) -> str:
        path = volumes[self.volume].to_path()
        return (path / self.path if self.path else path).as_posix()

    def to_input(self, resource: Resource) -> VolumePathInput:
        return VolumePathInput(volume=resource.volumes[self.volume], path=self.path)
