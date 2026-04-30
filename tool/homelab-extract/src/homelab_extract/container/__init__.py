from homelab_pydantic import HomelabRootModel

from .env import ContainerExtractEnvSource
from .info import ContainerExtractInfoSource
from .port import ContainerExtractPortSource
from .volume import ContainerExtractVolumeSource


class ContainerExtract(
    HomelabRootModel[
        ContainerExtractEnvSource
        | ContainerExtractInfoSource
        | ContainerExtractPortSource
        | ContainerExtractVolumeSource
    ]
):
    pass
