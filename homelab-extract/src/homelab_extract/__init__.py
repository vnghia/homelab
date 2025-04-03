from typing import Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from .container import ContainerExtract
from .docker import GlobalExtractDockerSource
from .hostname import GlobalExtractHostnameSource
from .id import GlobalExtractIdSource
from .json import GlobalExtractJsonSource
from .name import GlobalExtractNameSource
from .service import ServiceExtract, ServiceExtractSource
from .simple import GlobalExtractSimpleSource
from .transform import ExtractTransform
from .vpn import GlobalExtractVpnSource


class GlobalExtractSource(
    HomelabRootModel[
        GlobalExtractDockerSource
        | GlobalExtractHostnameSource
        | GlobalExtractIdSource
        | GlobalExtractJsonSource
        | GlobalExtractNameSource
        | GlobalExtractSimpleSource
        | GlobalExtractVpnSource
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
