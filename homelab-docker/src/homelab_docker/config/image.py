from pydantic import BaseModel

from homelab_docker.model.image import Remote as RemoteModel
from homelab_docker.model.platform import Model as Platform


class Image(BaseModel):
    platform: Platform
    remote: dict[str, RemoteModel]
