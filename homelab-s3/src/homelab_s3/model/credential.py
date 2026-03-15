from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from pydantic import HttpUrl


class S3CredentialEnvKey(HomelabBaseModel):
    key_id: str = "AWS_ACCESS_KEY_ID"
    access_key: str = "AWS_SECRET_ACCESS_KEY"
    region: str = "AWS_REGION"
    endpoint: str = "AWS_ENDPOINT_URL"


class S3CredentialModel(HomelabBaseModel):
    DEFAULT_ENV_KEY: ClassVar[S3CredentialEnvKey] = S3CredentialEnvKey()
    DEFAULT_ENDPOINT: ClassVar[HttpUrl] = HttpUrl("https://s3.amazonaws.com")

    key_id: str
    access_key: str
    region: str
    endpoint: HttpUrl | None = None

    def to_envs(self, env: S3CredentialEnvKey | None) -> dict[str, str]:
        env = env or self.DEFAULT_ENV_KEY
        return {
            env.key_id: self.key_id,
            env.access_key: self.access_key,
            env.region: self.region,
        } | ({env.endpoint: str(self.endpoint)} if self.endpoint else {})
