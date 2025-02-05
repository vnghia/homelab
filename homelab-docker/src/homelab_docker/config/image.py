from pydantic import BaseModel

from homelab_docker import model


class Image(BaseModel):
    platform: model.Platform
    remote: dict[str, model.RemoteImage]
