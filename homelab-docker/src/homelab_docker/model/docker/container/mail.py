from __future__ import annotations

import typing

from homelab_pydantic.model import HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ....extract import ExtractorArgs


class ContainerMailConfig(HomelabBaseModel):
    mail: str

    host: str | None = None
    port: str | None = None
    address: str | None = None
    username: str | None = None
    password: str | None = None

    def to_envs(self, extractor_args: ExtractorArgs) -> dict[str, Output[str]]:
        mail = extractor_args.global_args.mail[self.mail]

        return {
            k: Output.from_input(v)
            for k, v in (
                ({self.host: mail.host} if self.host else {})
                | ({self.port: str(mail.port)} if self.port else {})
                | ({self.address: mail.address} if self.address else {})
                | (
                    {self.username: mail.username or mail.address}
                    if self.username
                    else {}
                )
                | (
                    {self.password: '"{}"'.format(mail.password)}
                    if self.password
                    else {}
                )
            ).items()
        }
