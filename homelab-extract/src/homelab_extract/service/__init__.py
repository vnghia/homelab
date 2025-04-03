from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..container import ContainerExtract
from ..transform import ExtractTransform
from .export import ServiceExtractExportSource
from .keepass import ServiceExtractKeepassSource
from .secret import ServiceExtractSecretSource
from .variable import ServiceExtractVariableSource


class ServiceExtractSource(
    HomelabRootModel[
        ServiceExtractExportSource
        | ServiceExtractKeepassSource
        | ServiceExtractSecretSource
        | ServiceExtractVariableSource
    ]
):
    pass


class ServiceExtractFull(HomelabBaseModel):
    container: str | None = None
    extract: ContainerExtract | ServiceExtractSource
    transform: ExtractTransform = ExtractTransform()


class ServiceExtract(
    HomelabRootModel[ContainerExtract | ServiceExtractSource | ServiceExtractFull]
):
    @property
    def container(self) -> str | None:
        root = self.root

        return root.container if isinstance(root, ServiceExtractFull) else None
