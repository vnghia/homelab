from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from ..file import FilePermissionModel


class ServiceFileModel(HomelabBaseModel):
    active: bool = True
    bind: bool = True
    path: GlobalExtract
    content: GlobalExtract

    # TODO: Set owner based on container user
    permission: FilePermissionModel = FilePermissionModel()
