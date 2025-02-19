from homelab_pydantic import HomelabBaseModel
from pydantic import Field, HttpUrl


class S3Integration(HomelabBaseModel):
    key_id: str = Field(alias="key-id")
    access_key: str = Field(alias="access-key")
    region: str
    endpoint: HttpUrl | None = None

    def to_envs(self, use_default_region: bool) -> dict[str, str]:
        return {
            "AWS_ACCESS_KEY_ID": self.key_id,
            "AWS_SECRET_ACCESS_KEY": self.access_key,
            "AWS_DEFAULT_REGION" if use_default_region else "AWS_REGION": self.region,
        } | ({"AWS_ENDPOINT_URL": str(self.endpoint)} if self.endpoint else {})
