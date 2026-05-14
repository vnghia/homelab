from pathlib import PosixPath
from typing import Self

from homelab_pydantic import RelativePath
from homelab_pydantic.model import HomelabRootModel


class ExtractTransformPath(HomelabRootModel[RelativePath]):
    @classmethod
    def default(cls) -> Self:
        return cls(RelativePath(PosixPath("")))
