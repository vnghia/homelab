from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import HttpUrl, IPvAnyAddress

from .entrypoint import TraefikEntrypointConfig
from .log import TraefikLogConfig


class TraefikPathConfig(HomelabBaseModel):
    static: GlobalExtract
    dynamic: GlobalExtract
    api: GlobalExtract | None = None


class TraefikAcmeConfig(HomelabBaseModel):
    server: HttpUrl
    email: str
    storage: GlobalExtract
    disable_checks: bool
    require_all_rns: bool
    disable_ans_checks: bool
    delay_before_checks: str


class TraefikTimeoutConfig(HomelabBaseModel):
    read: str
    write: str
    idle: str


class TraefikProxyProtocolConfig(HomelabBaseModel):
    enabled: bool = False
    ips: list[IPvAnyAddress] = []


class TraefikPluginConfig(HomelabBaseModel):
    name: str
    version: str


class TraefikConfig(TraefikServiceConfigBase, HomelabBaseModel):
    path: TraefikPathConfig
    acme: TraefikAcmeConfig
    log: TraefikLogConfig
    entrypoint: TraefikEntrypointConfig
    plugins: dict[str, TraefikPluginConfig] = {}
