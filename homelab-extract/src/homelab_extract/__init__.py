from typing import Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from .container import ContainerExtract
from .dict_ import GlobalExtractDictSource
from .docker import GlobalExtractDockerSource
from .hostname import GlobalExtractHostnameSource
from .id import GlobalExtractIdSource
from .json import GlobalExtractJsonSource
from .kv import GlobalExtractKvSource
from .name import GlobalExtractNameSource
from .service import ServiceExtract, ServiceExtractSource
from .simple import GlobalExtractSimpleSource
from .transform import ExtractTransform
from .vpn import GlobalExtractVpnSource
from .yaml import GlobalExtractYamlSource


class GlobalExtractSource(
    HomelabRootModel[
        GlobalExtractDictSource
        | GlobalExtractDockerSource
        | GlobalExtractHostnameSource
        | GlobalExtractIdSource
        | GlobalExtractJsonSource
        | GlobalExtractKvSource
        | GlobalExtractNameSource
        | GlobalExtractSimpleSource
        | GlobalExtractVpnSource
        | GlobalExtractYamlSource
    ]
):
    pass


class GlobalExtractFull(HomelabBaseModel):
    service: str | None = None
    extract: ServiceExtract | GlobalExtractSource
    transform: ExtractTransform = ExtractTransform()


class GlobalExtract(
    HomelabRootModel[
        ContainerExtract
        | ServiceExtractSource
        | GlobalExtractSource
        | GlobalExtractFull
    ]
):
    @classmethod
    def from_simple(cls, value: str) -> Self:
        return cls(GlobalExtractSource(GlobalExtractSimpleSource(value)))


GlobalExtractSource.model_rebuild()
GlobalExtractFull.model_rebuild()
GlobalExtract.model_rebuild()
