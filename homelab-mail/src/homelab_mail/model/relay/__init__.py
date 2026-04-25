from homelab_pydantic import HomelabRootModel, Hostname
from pulumi import ResourceOptions

from .purelymail import MailRelayPurelyMailModel


class MailRelayModel(HomelabRootModel[MailRelayPurelyMailModel]):
    root: MailRelayPurelyMailModel

    def build_resource(
        self, key: str, opts: ResourceOptions, hostname: Hostname
    ) -> None:
        return self.root.build_resource(key, opts, hostname)
