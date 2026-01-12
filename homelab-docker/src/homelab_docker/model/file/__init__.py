from typing import ClassVar

from homelab_pydantic import HomelabBaseModel, RelativePath
from pydantic import NonNegativeInt, PositiveInt

from ..user import UidGidModel


class FileLocationModel(HomelabBaseModel):
    volume: str
    path: RelativePath

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())


class FilePermissionModel(HomelabBaseModel):
    DEFAULT_MODE: ClassVar[PositiveInt] = 0o400
    EXECUTABLE_MODE: ClassVar[PositiveInt] = 0o500

    DEFAULT_UID: ClassVar[NonNegativeInt] = 1000
    DEFAULT_GID: ClassVar[NonNegativeInt] = 1000

    mode: PositiveInt = DEFAULT_MODE
    owner: UidGidModel = UidGidModel()
