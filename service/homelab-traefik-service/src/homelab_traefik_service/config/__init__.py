from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_pydantic import HomelabBaseModel, RelativePath
from pydantic import Field, HttpUrl


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
    public_http: str = Field(alias="public-http")
    private_http: str = Field(alias="private-http")
    public_https: str = Field(alias="public-https")
    private_https: str = Field(alias="private-https")


class TraefikConfig(HomelabBaseModel):
    path: str
    acme: TraefikAcmeConfig
    provider: TraefikProviderConfig
    entrypoint: TraefikEntrypointConfig
