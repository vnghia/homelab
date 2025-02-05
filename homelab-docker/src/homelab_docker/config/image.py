from pydantic import BaseModel

from homelab_docker import model


class Image(BaseModel):
    remote: dict[str, model.RemoteImage]
