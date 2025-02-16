from pathlib import PosixPath
from typing import Self

from pydantic import BaseModel

from homelab_docker.pydantic import RelativePath

from .volume import ContainerVolumesConfig


class ContainerVolumePath(BaseModel):
    volume: str
    path: RelativePath = PosixPath("")

    def to_container_path(
        self, container_volumes_config: ContainerVolumesConfig
    ) -> PosixPath:
        path = container_volumes_config[self.volume].to_container_path()
        return path / self.path if self.path else path

    def join(self, path: RelativePath) -> Self:
        return self.model_copy(update={"path": self.path / path})

    def with_suffix(self, suffix: str) -> Self:
        return self.model_copy(update={"path": self.path.with_suffix(suffix)})
