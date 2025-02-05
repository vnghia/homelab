from pydantic import BaseModel

from homelab_docker.model.volume import Local as LocalModel


class Volume(BaseModel):
    local: dict[str, LocalModel]
