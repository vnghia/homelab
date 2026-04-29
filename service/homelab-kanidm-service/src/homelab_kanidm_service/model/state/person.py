from homelab_pydantic import HomelabBaseModel


class KanidmStatePersonModel(HomelabBaseModel):
    present: bool = True
    display_name: str
    legal_name: str | None = None
    mail_addresses: list[str] = []
    admin: bool = False
