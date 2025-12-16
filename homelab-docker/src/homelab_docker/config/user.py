from homelab_pydantic import HomelabServiceConfigDict

from ..model.user import UidGidModel


class UidGidConfig(HomelabServiceConfigDict[UidGidModel]):
    NONE_KEY = "user"
