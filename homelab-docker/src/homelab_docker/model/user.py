from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import NonNegativeInt


class UidGidModel(HomelabBaseModel):
    DEFAULT_UID: ClassVar[NonNegativeInt] = 1000
    DEFAULT_GID: ClassVar[NonNegativeInt] = 1000

    uid: NonNegativeInt = DEFAULT_UID
    gid: NonNegativeInt = DEFAULT_GID
