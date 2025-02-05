from pydantic import BaseModel

from homelab_docker import model


class Volume(BaseModel):
    local: dict[str, model.LocalVolume]
