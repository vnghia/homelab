from homelab_extract.service import ServiceExtract
from homelab_pydantic import HomelabBaseModel
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import HttpUrl, IPvAnyAddress


class TraefikPathConfig(HomelabBaseModel):
    static: ServiceExtract
    dynamic: ServiceExtract
    api: ServiceExtract


class TraefikAcmeConfig(HomelabBaseModel):
    server: HttpUrl
    email: str
    storage: ServiceExtract
    disable_checks: bool
    require_all_rns: bool
    disable_ans_checks: bool
    delay_before_checks: str


class TraefikEntrypointConfig(HomelabBaseModel):
    public_http: str
    private_http: str
    public_https: str
    private_https: str


class TraefikProxyProtocolConfig(HomelabBaseModel):
    ips: list[IPvAnyAddress] = []


class TraefikPluginConfig(HomelabBaseModel):
    name: str
    version: str


class TraefikConfig(TraefikServiceConfigBase, HomelabBaseModel):
    path: TraefikPathConfig
    acme: TraefikAcmeConfig
    entrypoint: TraefikEntrypointConfig
    timeout: str
    proxy_protocol: TraefikProxyProtocolConfig = TraefikProxyProtocolConfig()
    plugins: dict[str, TraefikPluginConfig] = {}
