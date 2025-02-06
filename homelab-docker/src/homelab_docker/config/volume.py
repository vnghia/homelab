from pydantic import BaseModel

from homelab_docker.model.volume import LocalVolumeModel


class VolumeConfig(BaseModel):
    local: dict[str, LocalVolumeModel]
