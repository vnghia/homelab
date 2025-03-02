from enum import StrEnum, auto

from homelab_docker.model.container.extract import ContainerExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class TraefikDynamicServiceType(StrEnum):
    HTTP = auto()


class TraefikDynamicServiceFullModel(HomelabBaseModel):
    container: str | None = None
    port: ContainerExtract


class TraefikDynamicServiceModel(
    HomelabRootModel[str | TraefikDynamicServiceFullModel]
):
    pass
