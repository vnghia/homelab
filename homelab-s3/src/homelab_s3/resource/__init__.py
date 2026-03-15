import dataclasses
from typing import ClassVar

from pulumi import ComponentResource, Output, ResourceOptions
from pydantic import HttpUrl

from ..config import S3Config
from ..model import S3CredentialEnvKey, S3Key, S3Type
from .b2 import B2Resource


@dataclasses.dataclass
class S3CredentialArgs:
    DEFAULT_ENV_KEY: ClassVar[S3CredentialEnvKey] = S3CredentialEnvKey()
    DEFAULT_ENDPOINT: ClassVar[HttpUrl] = HttpUrl("https://s3.amazonaws.com")

    key_id: Output[str]
    access_key: Output[str]
    region: Output[str] | None = None
    endpoint: HttpUrl | None = None

    bucket: Output[str] | None = None

    def to_envs(self, env: S3CredentialEnvKey | None) -> dict[str, Output[str]]:
        env = env or self.DEFAULT_ENV_KEY
        return (
            {
                env.key_id: self.key_id,
                env.access_key: self.access_key,
            }
            | ({env.region: Output.from_input(self.region)} if self.region else {})
            | (
                {env.endpoint: Output.from_input(str(self.endpoint))}
                if self.endpoint
                else {}
            )
            | ({env.bucket: self.bucket} if self.bucket else {})
        )


@dataclasses.dataclass
class S3Credentials:
    root: dict[S3Type, dict[str, S3CredentialArgs]]

    def __getitem__(self, key: S3Key) -> S3CredentialArgs:
        return self.root[key.type][key.name]


class S3Resource(ComponentResource):
    RESOURCE_NAME = "s3"

    def __init__(self, config: S3Config, *, opts: ResourceOptions | None) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.custom = {
            k: S3CredentialArgs(
                key_id=Output.from_input(v.key_id),
                access_key=Output.from_input(v.access_key),
                region=Output.from_input(v.region) if v.region else None,
                endpoint=v.endpoint,
            )
            for k, v in config.custom.root.items()
        }
        self.b2 = B2Resource(config.b2, opts=self.child_opts)

        self.credentials = S3Credentials(
            root={S3Type.CUSTOM: self.custom, S3Type.B2: self.b2.credentials}
        )
        self.register_outputs({})
