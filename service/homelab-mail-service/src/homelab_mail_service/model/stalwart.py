from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class MailStalwartListenerModel(HomelabBaseModel):
    port: GlobalExtract
    protocol: str
    use_tls: bool = False
    implicit_tls: bool = False
