from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..service import ServiceExtract
from ..transform import ExtractTransform
from .info import HostExtractInfoSource
from .network import HostExtractNetworkSource
from .variable import HostExtractVariableSource


class HostExtractSource(
    HomelabRootModel[
        HostExtractInfoSource | HostExtractNetworkSource | HostExtractVariableSource
    ]
):
    pass


class HostExtractFull(HomelabBaseModel):
    service: str | None = None
    extract: ServiceExtract | HostExtractSource
    transform: ExtractTransform | None = None


class HostExtract(
    HomelabRootModel[HostExtractFull | HostExtractSource | ServiceExtract]
):
    def to_full(self) -> HostExtractFull:
        root = self.root
        if isinstance(root, HostExtractFull):
            return root
        return HostExtractFull(extract=root)

    def with_service(self, service: str, force: bool) -> HostExtract:
        full = self.to_full()
        if not force:
            service = full.service or service
        return self.__class__.model_construct(
            full.model_copy(update={"service": service})
        )
