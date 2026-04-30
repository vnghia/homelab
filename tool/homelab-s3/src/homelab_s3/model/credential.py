from homelab_pydantic import HomelabBaseModel
from pydantic import HttpUrl


class S3CredentialModel(HomelabBaseModel):
    key_id: str
    access_key: str
    region: str | None = None
    endpoint: HttpUrl | None = None
