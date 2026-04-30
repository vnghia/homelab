from pathlib import PosixPath

from homelab_pydantic import RelativePath
from homelab_pydantic.model import HomelabRootModel


class ExtractTransformPath(HomelabRootModel[RelativePath]):
    root: RelativePath = RelativePath(PosixPath(""))
