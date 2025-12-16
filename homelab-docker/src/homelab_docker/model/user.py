from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import NonNegativeInt


class UidGidModel(HomelabBaseModel):
    NOBODY_UID: ClassVar[NonNegativeInt] = 65534
    NOGROUP_GID: ClassVar[NonNegativeInt] = 65534

    uid: NonNegativeInt = NOBODY_UID
    gid: NonNegativeInt = NOGROUP_GID

    def container(self) -> str:
        return "{}:{}".format(self.uid, self.gid)
