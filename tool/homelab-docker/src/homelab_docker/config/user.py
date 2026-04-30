from typing import ClassVar

from homelab_pydantic import HomelabServiceConfigDict

from ..model.user import UidGidModel


class UidGidConfig(HomelabServiceConfigDict[UidGidModel]):
    NONE_KEY = "user"

    DOCKER_KEY: ClassVar[str] = "docker"
