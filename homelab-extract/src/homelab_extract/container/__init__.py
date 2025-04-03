from homelab_pydantic import HomelabRootModel

from .env import ContainerExtractEnvSource
from .volume import ContainerExtractVolumeSource


class ContainerExtract(
    HomelabRootModel[ContainerExtractEnvSource | ContainerExtractVolumeSource]
):
    pass
