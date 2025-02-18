from __future__ import annotations

from pathlib import PosixPath

from homelab_pydantic import HomelabBaseModel, RelativePath

from .volume import ContainerVolumesConfig


class ContainerVolumePath(HomelabBaseModel):
    volume: str
    path: RelativePath = PosixPath("")

    def to_container_path(
        self, container_volumes_config: ContainerVolumesConfig
    ) -> PosixPath:
        path = container_volumes_config[self.volume].to_container_path()
        return path / self.path if self.path else path

    def join(self, path: RelativePath) -> ContainerVolumePath:
        return self.__replace__(path=self.path / path)

    def with_suffix(self, suffix: str) -> ContainerVolumePath:
        return self.__replace__(path=self.path.with_suffix(suffix))
