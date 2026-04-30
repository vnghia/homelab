from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ..file import FilePermissionModel


class ServiceFileModel(HomelabBaseModel):
    active: bool = True
    bind: bool = True
    path: GlobalExtract
    content: GlobalExtract
    mode: PositiveInt = FilePermissionModel.DEFAULT_MODE
