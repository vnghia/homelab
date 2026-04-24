import dataclasses

import pulumi_random as random
from homelab_pydantic import Hostnames
from pulumi import ComponentResource, Output, ResourceOptions

from ..config import MailConfig


@dataclasses.dataclass
class NoReplyAccountArgs:
    username: str
    domain: str
    password: random.RandomPassword

    @property
    def address(self) -> str:
        return "{}@{}".format(self.username, self.domain)


class NoReplyResource(ComponentResource):
    RESOURCE_NAME = "no-reply"

    def __init__(
        self,
        config: MailConfig,
        *,
        opts: ResourceOptions | None,
        host: str,
        hostnames: Hostnames,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self, delete_before_replace=True)
        self.accounts = {}
        self.credentials = {}

        from ..resource import MailCredentialArgs

        for name, model in config.noreply.root.items():
            account = NoReplyAccountArgs(
                username=model.username,
                domain=hostnames[model.record][model.hostname or name].value,
                password=random.RandomPassword(
                    name,
                    opts=self.child_opts,
                    length=64,
                    override_special="!@$%&*()-_=+[]<>?",
                ),
            )

            self.accounts[name] = account
            self.credentials[name] = MailCredentialArgs(
                host=Output.from_input(host),
                port=config.address.port[model.port],
                address=Output.from_input(account.address),
                password=account.password.result,
                username=None,
            )

        self.register_outputs({})
