from __future__ import annotations

import typing

from homelab_pydantic.model import HomelabBaseModel
from homelab_s3.model import S3CredentialEnvKey, S3Key
from pulumi import Output

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerS3Config(HomelabBaseModel):
    key: S3Key
    env: S3CredentialEnvKey | None = None

    def build_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        return extractor_args.global_resource.plain_args.s3[self.key].to_envs(self.env)
