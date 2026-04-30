from typing import ClassVar

from homelab_extract.plain import PlainArgs
from homelab_pydantic import HomelabBaseModel
from pulumi import Output


class ResticHostBase(HomelabBaseModel):
    SCHEME: ClassVar[str]

    path: str = "backup/restic"

    def build_prefix(self, plain_args: PlainArgs) -> str | Output[str]:
        return Output.from_input("")

    def build_repository(self, plain_args: PlainArgs) -> Output[str]:
        return Output.concat(self.SCHEME, ":", self.build_prefix(plain_args), self.path)

    def build_envs(self, plain_args: PlainArgs) -> dict[str, Output[str]]:
        return {}
