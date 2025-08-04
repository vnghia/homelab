from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_pydantic import AbsolutePath, HomelabBaseModel, RelativePath

if typing.TYPE_CHECKING:
    from ...extract import ExtractorArgs


class ContainerVolumePath(HomelabBaseModel):
    volume: str
    path: RelativePath = RelativePath(PosixPath(""))

    def to_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        path = extractor_args.container.volumes[self.volume].to_path(extractor_args)
        return path / self.path if self.path else path

    def __truediv__(self, path: str | RelativePath) -> ContainerVolumePath:
        return self.__replace__(path=self.path / path)

    def with_suffix(self, suffix: str) -> ContainerVolumePath:
        return self.__replace__(path=self.path.with_suffix(suffix))

    def __json__(self) -> str:
        raise TypeError("Could not serialize {} to JSON".format(self))
