import dataclasses

from homelab_pydantic import Hostnames
from pulumi import ComponentResource, Output, ResourceOptions
from pydantic import PositiveInt

from homelab_mail.config import MailConfig
from homelab_mail.resource.no_reply import NoReplyResource

from ..model import MailCredentialEnvKey, MailKey, MailType


@dataclasses.dataclass
class MailCredentialArgs:
    host: Output[str]
    port: PositiveInt
    address: Output[str]
    password: Output[str]
    username: Output[str] | None = None

    def to_envs(self, env: MailCredentialEnvKey) -> dict[str, Output[str]]:
        return {
            env.host: self.host,
            env.port: Output.from_input(str(self.port)),
            env.address: self.address,
            env.password: Output.format('"{}"', self.password),
        } | ({env.username: self.username or self.address} if env.username else {})


@dataclasses.dataclass
class MailCredentials:
    root: dict[MailType, dict[str, MailCredentialArgs]]

    def __getitem__(self, key: MailKey) -> MailCredentialArgs:
        return self.root[key.type][key.name]


class MailResource(ComponentResource):
    RESOURCE_NAME = "mail"

    def __init__(
        self, config: MailConfig, *, opts: ResourceOptions | None, hostnames: Hostnames
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)
        self.config = config

        self.custom = {
            k: MailCredentialArgs(
                host=Output.from_input(v.host),
                port=v.port,
                address=Output.from_input(v.address),
                password=Output.from_input(v.password),
                username=Output.from_input(v.username) if v.username else None,
            )
            for k, v in config.custom.root.items()
        }
        self.no_reply = NoReplyResource(
            config, opts=self.child_opts, hostnames=hostnames
        )

        self.credentials = MailCredentials(root={MailType.CUSTOM: self.custom})
        self.register_outputs({})
