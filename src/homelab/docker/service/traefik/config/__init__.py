from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.pydantic import RelativePath
from pydantic import BaseModel, Field, HttpUrl


class TraefikAcmeStorageConfig(BaseModel):
    public: ContainerVolumePath
    private: ContainerVolumePath


class TraefikAcmeConfig(BaseModel):
    server: HttpUrl
    email: str
    storage: TraefikAcmeStorageConfig


class TraefikProviderConfig(BaseModel):
    file: RelativePath


class TraefikEntrypointConfig(BaseModel):
    public_http: str = Field(alias="public-http")
    private_http: str = Field(alias="private-http")
    public_https: str = Field(alias="public-https")
    private_https: str = Field(alias="private-https")


class TraefikConfig(BaseModel):
    path: str
    acme: TraefikAcmeConfig
    provider: TraefikProviderConfig
    entrypoint: TraefikEntrypointConfig
