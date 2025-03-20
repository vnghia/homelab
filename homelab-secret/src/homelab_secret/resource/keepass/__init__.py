import os
import uuid
from typing import Any

from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel
from pulumi import ResourceOptions
from pulumi.dynamic import (
    ConfigureRequest,
    CreateResult,
    DiffResult,
    ReadResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import HttpUrl
from pykeepass import PyKeePass
from pykeepass.group import Group


class KeepassEntryProps(HomelabBaseModel):
    username: str
    email: str | None
    password: str
    hostname: HttpUrl
    urls: list[HttpUrl]
    apps: list[str]


class KeepassProviderProps(HomelabRootModel[dict[str, KeepassEntryProps]]):
    @classmethod
    def open(cls) -> Group | None:
        filename = os.environ.get("KEEPASS_DATABASE")
        if filename:
            database = PyKeePass(
                filename,
                password=os.environ.get("KEEPASS_PASSWORD"),
                keyfile=os.environ.get("KEEPASS_KEYFILE"),
            )
            group = database.find_groups(
                uuid=uuid.UUID(hex=os.environ["KEEPASS_GROUP"]), first=True
            )
            assert isinstance(group, Group)
            return group
        else:
            return None


class KeepassProvider(ResourceProvider):
    serialize_as_secret_always = False


class KeepassResousrce(Resource, module="keepass", name="Keepass"):
    def __init__(self, *, opts: ResourceOptions | None):
        super().__init__(KeepassProvider(), self.__class__._name, {}, opts)
