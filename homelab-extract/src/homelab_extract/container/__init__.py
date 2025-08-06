from homelab_pydantic import HomelabRootModel

from .env import ContainerExtractEnvSource
from .id import ContainerExtractIdSource
from .name import ContainerExtractNameSource
from .volume import ContainerExtractVolumeSource


class ContainerExtract(
    HomelabRootModel[
        ContainerExtractEnvSource
        | ContainerExtractIdSource
        | ContainerExtractNameSource
        | ContainerExtractVolumeSource
    ]
):
    pass
