from homelab_pydantic import HomelabRootModel, Hostname
from pulumi import ResourceOptions

from ..credential import MailCredentialModel
from .purelymail import MailRelayPurelyMailModel


class MailRelayModel(HomelabRootModel[MailRelayPurelyMailModel]):
    root: MailRelayPurelyMailModel

    @property
    def credential(self) -> MailCredentialModel:
        return self.root.credential

    def build_resource(
        self, key: str, opts: ResourceOptions, hostname: Hostname
    ) -> None:
        return self.root.build_resource(key, opts, hostname)
