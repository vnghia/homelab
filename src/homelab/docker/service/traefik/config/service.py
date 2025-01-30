from homelab_docker.pydantic.path import RelativePath
from pydantic import BaseModel, ConfigDict, Field


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

    provider: Provider
    api: str
    entrypoint: Entrypoint
