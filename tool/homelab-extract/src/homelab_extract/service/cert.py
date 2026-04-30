from homelab_pydantic import HomelabBaseModel


class ServiceExtractCertSource(HomelabBaseModel):
    cert: str
