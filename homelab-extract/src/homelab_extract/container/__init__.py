from homelab_pydantic import HomelabRootModel

from .env import ContainerExtractEnvSource
from .info import ContainerExtractInfoSource
from .volume import ContainerExtractVolumeSource


class ContainerExtract(
    HomelabRootModel[
        ContainerExtractEnvSource
        | ContainerExtractInfoSource
        | ContainerExtractVolumeSource
    ]
):
    pass
