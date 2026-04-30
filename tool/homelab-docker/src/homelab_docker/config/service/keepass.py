from homelab_pydantic import HomelabServiceConfigDict
from homelab_secret.model.keepass.entry import KeepassEntryModel


class ServiceKeepassConfig(HomelabServiceConfigDict[KeepassEntryModel]):
    NONE_KEY = "keepass"
