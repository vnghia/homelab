from pathlib import PosixPath
from typing import ClassVar

from homelab_extract.plain import PlainArgs
from homelab_pydantic import AbsolutePath

from .base import ResticHostBase


class ResticSftpHost(ResticHostBase):
    SCHEME: ClassVar[str] = "sftp"

    sftp: str
    user: str
    prefix: AbsolutePath = AbsolutePath(PosixPath("/"))

    def build_prefix(self, plain_args: PlainArgs) -> str:
        return "//{}@{}/{}/".format(self.user, self.sftp, self.prefix.as_posix())
