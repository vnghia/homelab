from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class TraefikDynamicTlsCertificateModel(HomelabBaseModel):
    cert: GlobalExtract
    key: GlobalExtract


class TraefikDynamicTlsMultualModel(HomelabBaseModel):
    cas: list[GlobalExtract]


class TraefikDynamicTlsModel(HomelabBaseModel):
    active: bool = True
    name: str | None = None
    certs: list[TraefikDynamicTlsCertificateModel] = []
    mtls: TraefikDynamicTlsMultualModel | None = None
