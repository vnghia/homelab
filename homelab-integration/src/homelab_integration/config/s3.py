from pydantic import BaseModel, Field, HttpUrl


class S3IntegrationConfig(BaseModel):
    bucket: str
    key_id: str = Field(alias="key-id")
    access_key: str = Field(alias="access-key")
    region: str
    endpoint: HttpUrl

    def to_env(self) -> dict[str, str]:
        return {
            "AWS_ACCESS_KEY_ID": self.key_id,
            "AWS_SECRET_ACCESS_KEY": self.access_key,
            "AWS_REGION": self.region,
            "AWS_ENDPOINT_URL": str(self.endpoint),
        }
