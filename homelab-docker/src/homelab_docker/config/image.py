from pydantic import BaseModel, PositiveInt

from homelab_docker.model.image import RemoteImageModel
from homelab_docker.model.platform import Platform


class ImageConfig(BaseModel):
    platform: Platform
    remote: dict[str, RemoteImageModel]
    postgres: dict[str, dict[PositiveInt, RemoteImageModel]]
