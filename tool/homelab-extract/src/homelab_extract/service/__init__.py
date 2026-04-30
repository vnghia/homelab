from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..container import ContainerExtract
from ..transform import ExtractTransform
from .cert import ServiceExtractCertSource
from .database import ServiceExtractDatabaseSource
from .export import ServiceExtractExportSource
from .keepass import ServiceExtractKeepassSource
from .key import ServiceExtractKeySource
from .mtls import ServiceExtractMTlsSource
from .secret import ServiceExtractSecretSource
from .variable import ServiceExtractVariableSource
from .volume import ServiceExtractVolumeSource
from .vpn import ServiceExtractVpnSource


class ServiceExtractSource(
    HomelabRootModel[
        ServiceExtractCertSource
        | ServiceExtractDatabaseSource
        | ServiceExtractExportSource
        | ServiceExtractKeepassSource
        | ServiceExtractKeySource
        | ServiceExtractMTlsSource
        | ServiceExtractSecretSource
        | ServiceExtractVariableSource
        | ServiceExtractVolumeSource
        | ServiceExtractVpnSource
    ]
):
    pass


class ServiceContainerExtractFull(HomelabBaseModel):
    service: str | None = None
    container: str | None = None


class ServiceExtractFull(HomelabBaseModel):
    container: str | ServiceContainerExtractFull | None = None
    extract: ContainerExtract | ServiceExtractSource
    transform: ExtractTransform | None = None

    @property
    def has_container(self) -> bool:
        return "container" in self.model_fields_set


class ServiceExtract(
    HomelabRootModel[ServiceExtractFull | ServiceExtractSource | ContainerExtract]
):
    @property
    def container(self) -> str | None:
        root = self.root
        if isinstance(root, ServiceExtractFull):
            if isinstance(root.container, ServiceContainerExtractFull):
                raise ValueError("Context switching is required")
            return root.container
        return None
