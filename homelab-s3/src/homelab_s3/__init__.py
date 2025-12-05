from typing import ClassVar

from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel
from pydantic import HttpUrl


class S3Credential(HomelabBaseModel):
    DEFAULT_ENDPOINT: ClassVar[HttpUrl] = HttpUrl("https://s3.amazonaws.com/")

    key_id: str
    access_key: str
    region: str
    endpoint: HttpUrl | None = None

    def to_envs(self) -> dict[str, str]:
        return {
            "AWS_ACCESS_KEY_ID": self.key_id,
            "AWS_SECRET_ACCESS_KEY": self.access_key,
            "AWS_REGION": self.region,
        } | ({"AWS_ENDPOINT_URL": str(self.endpoint)} if self.endpoint else {})


class S3Config(HomelabRootModel[dict[str, S3Credential]]):
    root: dict[str, S3Credential] = {}

    def __getitem__(self, key: str) -> S3Credential:
        return self.root[key]
