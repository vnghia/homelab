from typing import ClassVar

from homelab_extract.plain import PlainArgs
from homelab_s3.model import S3Key
from pulumi import Output

from .base import ResticHostBase


class ResticS3Host(ResticHostBase):
    SCHEME: ClassVar[str] = "s3"

    s3: S3Key
    bucket: str | None = None

    def build_prefix(self, plain_args: PlainArgs) -> Output[str]:
        s3 = plain_args.s3[self.s3]
        bucket = self.bucket or s3.bucket
        if not bucket:
            raise ValueError("Bucket must be configured for s3 restic host")
        return Output.concat(
            (s3.endpoint or s3.DEFAULT_ENDPOINT).encoded_string(), bucket, "/"
        )

    def build_envs(self, plain_args: PlainArgs) -> dict[str, Output[str]]:
        return plain_args.s3[self.s3].to_envs(None)
