from homelab_docker.interpolation.container_volume_path import ContainerVolumePath
from homelab_docker.pydantic.path import RelativePath
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class Acme(BaseModel):
    model_config = ConfigDict(strict=True)

    server: HttpUrl
    email: str
    storage: ContainerVolumePath


class Provider(BaseModel):
    model_config = ConfigDict(strict=True)

    file: RelativePath


class Entrypoint(BaseModel):
    model_config = ConfigDict(strict=True)

    public_http: str = Field(alias="public-http")
    private_http: str = Field(alias="private-http")
    public_https: str = Field(alias="public-https")
    private_https: str = Field(alias="private-https")


class Service(BaseModel):
    model_config = ConfigDict(strict=True)

    path: str
    acme: Acme
    provider: Provider
    entrypoint: Entrypoint
