from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import HttpUrl, IPvAnyAddress


class TraefikPathConfig(HomelabBaseModel):
    static: GlobalExtract
    dynamic: GlobalExtract
    api: GlobalExtract


class TraefikAcmeConfig(HomelabBaseModel):
    server: HttpUrl
    email: str
    storage: GlobalExtract
    disable_checks: bool
    require_all_rns: bool
    disable_ans_checks: bool
    delay_before_checks: str


class TraefikEntrypointConfig(HomelabBaseModel):
    public_http: str
    private_http: str
    public_https: str
    private_https: str


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
    entrypoint: TraefikEntrypointConfig
    timeout: TraefikTimeoutConfig
    proxy_protocol: TraefikProxyProtocolConfig = TraefikProxyProtocolConfig()
    plugins: dict[str, TraefikPluginConfig] = {}
