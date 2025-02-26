from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict
from pydantic import Field, HttpUrl


class S3Config(HomelabBaseModel):
    key_id: str = Field(alias="key-id")
    access_key: str = Field(alias="access-key")
    region: str
    endpoint: HttpUrl | None = None

    def to_envs(self) -> dict[str, str]:
        return {
            "AWS_ACCESS_KEY_ID": self.key_id,
            "AWS_SECRET_ACCESS_KEY": self.access_key,
            "AWS_REGION": self.region,
        } | ({"AWS_ENDPOINT_URL": str(self.endpoint)} if self.endpoint else {})


class S3ServiceConfig(HomelabServiceConfigDict[S3Config]):
    def to_envs(self) -> dict[str | None, dict[str, str]]:
        return {name: config.to_envs() for name, config in self.root.items()}
