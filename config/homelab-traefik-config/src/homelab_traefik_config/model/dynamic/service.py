from enum import StrEnum, auto

from homelab_docker.extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class TraefikDynamicServiceType(StrEnum):
    HTTP = auto()


class TraefikDynamicServiceFullModel(HomelabBaseModel):
    container: str | None = None
    port: GlobalExtract


class TraefikDynamicServiceModel(
    HomelabRootModel[str | TraefikDynamicServiceFullModel]
):
    pass
