from typing import ClassVar

from homelab_extract.plain import PlainArgs

from .base import ResticHostBase


class ResticS3Host(ResticHostBase):
    SCHEME: ClassVar[str] = "s3"

    s3: str
    bucket: str

    def build_prefix(self, plain_args: PlainArgs) -> str:
        s3 = plain_args.s3[self.s3]
        return (s3.endpoint or s3.DEFAULT_ENDPOINT).encoded_string() + self.bucket + "/"

    def build_envs(self, plain_args: PlainArgs) -> dict[str, str]:
        return plain_args.s3[self.s3].to_envs()
