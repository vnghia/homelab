from __future__ import annotations

import typing

from homelab_mail.model import MailCredentialEnvKey, MailKey
from homelab_pydantic.model import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerMailConfig(HomelabBaseModel):
    key: MailKey
    env: MailCredentialEnvKey

    def build_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        return extractor_args.global_resource.plain_args.mail[self.key].to_envs(
            self.env
        )
