from homelab_pydantic import HomelabBaseModel

from ..credential import MailCredentialModel


class MailRelayBaseModel(HomelabBaseModel):
    credential: MailCredentialModel
