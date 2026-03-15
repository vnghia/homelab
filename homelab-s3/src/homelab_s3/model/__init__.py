from enum import StrEnum, auto

from homelab_pydantic import HomelabBaseModel


class S3Type(StrEnum):
    CUSTOM = auto()
    B2 = auto()


class S3Key(HomelabBaseModel):
    type: S3Type
    name: str


class S3CredentialEnvKey(HomelabBaseModel):
    key_id: str = "AWS_ACCESS_KEY_ID"
    access_key: str = "AWS_SECRET_ACCESS_KEY"
    region: str = "AWS_REGION"
    endpoint: str = "AWS_ENDPOINT_URL"
    bucket: str = "AWS_BUCKET"
