from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class KanidmStatePersonModel(HomelabBaseModel):
    present: bool = True
    display_name: GlobalExtract
    legal_name: GlobalExtract | None = None
    mail_addresses: list[GlobalExtract] = []
