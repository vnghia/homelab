from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pydantic import IPvAnyAddress


class TraefikDynamicServiceFullModel(HomelabBaseModel):
    container: str | None = None
    external: IPvAnyAddress | GlobalExtract | None = None
    port: GlobalExtract | None
    scheme: str | None = None
    pass_host_header: bool | None = None

    @property
    def port_(self) -> GlobalExtract:
        if self.port is None:
            raise ValueError("Traefik service port is not configured")
        return self.port


class TraefikDynamicServiceModel(
    HomelabRootModel[str | TraefikDynamicServiceFullModel]
):
    pass
