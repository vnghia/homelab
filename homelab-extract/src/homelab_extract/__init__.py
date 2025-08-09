from typing import Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from .dict_ import GlobalExtractDictSource
from .host import HostExtract
from .hostname import GlobalExtractHostnameSource
from .json import GlobalExtractJsonSource
from .kv import GlobalExtractKvSource
from .project import GlobalExtractProjectSource
from .simple import GlobalExtractSimpleSource
from .transform import ExtractTransform
from .yaml import GlobalExtractYamlSource


class GlobalExtractSource(
    HomelabRootModel[
        GlobalExtractDictSource
        | GlobalExtractHostnameSource
        | GlobalExtractJsonSource
        | GlobalExtractKvSource
        | GlobalExtractProjectSource
        | GlobalExtractSimpleSource
        | GlobalExtractYamlSource
    ]
):
    pass


class GlobalExtractFull(HomelabBaseModel):
    host: str | None = None
    extract: HostExtract | GlobalExtractSource
    transform: ExtractTransform = ExtractTransform()


class GlobalExtract(
    HomelabRootModel[GlobalExtractFull | GlobalExtractSource | HostExtract]
):
    @classmethod
    def from_simple(cls, value: str) -> Self:
        return cls(GlobalExtractSource(GlobalExtractSimpleSource(value)))


GlobalExtractSource.model_rebuild()
GlobalExtractFull.model_rebuild()
GlobalExtract.model_rebuild()
