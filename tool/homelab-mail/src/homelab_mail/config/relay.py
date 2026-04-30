from homelab_pydantic import HomelabRootModel

from ..model.relay import MailRelayModel


class MailRelayConfig(HomelabRootModel[dict[str, MailRelayModel]]):
    root: dict[str, MailRelayModel] = {}
