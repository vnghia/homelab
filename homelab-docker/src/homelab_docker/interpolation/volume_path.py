from pathlib import PosixPath

from homelab_docker.model.container.volume import Volume as ContainerVolume
from homelab_docker.pydantic.path import RelativePath
from pydantic import BaseModel


class VolumePath(BaseModel):
    volume: str
    path: RelativePath = PosixPath("")

    def to_container_path(
        self, container_volumes: dict[str, ContainerVolume]
    ) -> PosixPath:
        path = container_volumes[self.volume].to_container_path()
        return path / self.path if self.path else path
