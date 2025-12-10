from typing import ClassVar

from homelab_extract.plain import PlainArgs
from homelab_pydantic import HomelabBaseModel


class ResticHostBase(HomelabBaseModel):
    SCHEME: ClassVar[str]

    path: str = "backup/restic"

    def build_prefix(self, plain_args: PlainArgs) -> str:
        return ""

    def build_repository(self, plain_args: PlainArgs) -> str:
        return self.SCHEME + ":" + self.build_prefix(plain_args) + self.path

    def build_envs(self, plain_args: PlainArgs) -> dict[str, str]:
        return {}
