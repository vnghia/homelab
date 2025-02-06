from pathlib import PosixPath

from pydantic import BaseModel

from homelab_docker.model.container.volume import ContainerVolumesConfig
from homelab_docker.pydantic.path import RelativePath


class ContainerVolumePath(BaseModel):
    volume: str
    path: RelativePath = PosixPath("")

    def to_container_path(
        self, container_volumes_config: ContainerVolumesConfig
    ) -> PosixPath:
        path = container_volumes_config[self.volume].to_container_path()
        return path / self.path if self.path else path
