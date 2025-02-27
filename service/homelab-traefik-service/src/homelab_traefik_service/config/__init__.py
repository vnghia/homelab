from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_pydantic import HomelabBaseModel, RelativePath
from pydantic import HttpUrl, IPvAnyAddress


class TraefikAcmeStorageConfig(HomelabBaseModel):
    public: ContainerVolumePath
    private: ContainerVolumePath


class TraefikAcmeConfig(HomelabBaseModel):
    server: HttpUrl
    email: str
    storage: TraefikAcmeStorageConfig


class TraefikProviderConfig(HomelabBaseModel):
    file: RelativePath


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


class TraefikConfig(HomelabBaseModel):
    path: str
    acme: TraefikAcmeConfig
    provider: TraefikProviderConfig
    entrypoint: TraefikEntrypointConfig
    proxy_protocol: TraefikProxyProtocolConfig = TraefikProxyProtocolConfig()
    plugins: dict[str, TraefikPluginConfig] = {}
