from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class ResticHostBase(HomelabBaseModel):
    SCHEME: ClassVar[str]

    path: str

    @property
    def repository(self) -> str:
        return self.SCHEME + ":" + self.path
