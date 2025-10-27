from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..service import ServiceExtract
from ..transform import ExtractTransform
from .info import HostExtractInfoSource
from .variable import HostExtractVariableSource


class HostExtractSource(
    HomelabRootModel[HostExtractInfoSource | HostExtractVariableSource]
):
    pass


class HostExtractFull(HomelabBaseModel):
    service: str | None = None
    extract: ServiceExtract | HostExtractSource
    transform: ExtractTransform | None = None


class HostExtract(
    HomelabRootModel[HostExtractFull | HostExtractSource | ServiceExtract]
):
    pass
