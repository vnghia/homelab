from enum import StrEnum, auto

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pydantic import IPvAnyAddress


class TraefikDynamicServiceType(StrEnum):
    HTTP = auto()


class TraefikDynamicServiceFullModel(HomelabBaseModel):
    container: str | None = None
    external: IPvAnyAddress | str | None = None
    port: GlobalExtract
    scheme: str | None = None
    pass_host_header: bool | None = None


class TraefikDynamicServiceModel(
    HomelabRootModel[str | TraefikDynamicServiceFullModel]
):
    pass
