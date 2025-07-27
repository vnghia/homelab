from homelab_pydantic import HomelabBaseModel

from ..model.volume import LocalVolumeModel


class VolumeConfig(HomelabBaseModel):
    local: dict[str, LocalVolumeModel] = {}
