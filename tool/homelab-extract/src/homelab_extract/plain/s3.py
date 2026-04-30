from __future__ import annotations

import typing
from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel
from homelab_s3.model import S3Key
from pulumi import Output

if typing.TYPE_CHECKING:
    from . import PlainArgs


class S3InfoSource(StrEnum):
    BUCKET = auto()


class GlobalPlainExtractS3Source(HomelabBaseModel):
    s3: S3Key
    info: S3InfoSource

    def extract_str(self, plain_args: PlainArgs) -> Output[str]:
        match self.info:
            case S3InfoSource.BUCKET:
                bucket = plain_args.s3[self.s3].bucket
                if not bucket:
                    raise ValueError(
                        "Bucket is not configured for this s3 key {}".format(self.s3)
                    )
                return bucket
