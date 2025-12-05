from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt


class ServiceFileModel(HomelabBaseModel):
    active: bool = True
    bind: bool = True
    path: GlobalExtract
    mode: PositiveInt | None = None
    content: GlobalExtract
