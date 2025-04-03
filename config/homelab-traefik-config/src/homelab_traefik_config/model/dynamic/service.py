from enum import StrEnum, auto

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class TraefikDynamicServiceType(StrEnum):
    HTTP = auto()


class TraefikDynamicServiceFullModel(HomelabBaseModel):
    container: str | None = None
    port: GlobalExtract
    scheme: str | None = None


class TraefikDynamicServiceModel(
    HomelabRootModel[str | TraefikDynamicServiceFullModel]
):
    pass
