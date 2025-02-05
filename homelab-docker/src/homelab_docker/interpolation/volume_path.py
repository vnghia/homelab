from pathlib import PosixPath

from pydantic import BaseModel

from homelab_docker.model.container.volume import Volumes as ContainerVolumes
from homelab_docker.pydantic.path import RelativePath


class VolumePath(BaseModel):
    volume: str
    path: RelativePath = PosixPath("")

    def to_container_path(self, container_volumes: ContainerVolumes) -> PosixPath:
        path = container_volumes[self.volume].to_container_path()
        return path / self.path if self.path else path
