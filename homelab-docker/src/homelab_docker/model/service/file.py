from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel

from ...model.file import FilePermissionUserModel


class ServiceFileModel(HomelabBaseModel):
    active: bool = True
    bind: bool = True
    path: GlobalExtract
    content: GlobalExtract
    permission: FilePermissionUserModel = FilePermissionUserModel()
