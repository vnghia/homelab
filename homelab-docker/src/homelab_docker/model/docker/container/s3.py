from __future__ import annotations

import typing

from homelab_pydantic.model import HomelabBaseModel
from homelab_s3 import S3CredentialEnvKey

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerS3Config(HomelabBaseModel):
    config: str
    env: S3CredentialEnvKey | None = None

    def build_envs(self, extractor_args: ExtractorArgs) -> dict[str, str]:
        return extractor_args.global_resource.config.s3[self.config].to_envs(self.env)
