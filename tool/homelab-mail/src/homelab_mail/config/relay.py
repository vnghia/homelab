from typing import Self

from homelab_pydantic import HomelabRootModel

from ..model.relay import MailRelayModel


class MailRelayConfig(HomelabRootModel[dict[str, MailRelayModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})
