from pydantic import BaseModel

from ..model.volume import LocalVolumeModel


class VolumeConfig(BaseModel):
    local: dict[str, LocalVolumeModel]
