import os
import uuid
from contextlib import contextmanager
from typing import Any, Iterator

from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel
from pulumi.dynamic import (
    CreateResult,
    DiffResult,
    ReadResult,
    Resource,
    ResourceProvider,
    UpdateResult,
)
from pydantic import HttpUrl
from pykeepass import PyKeePass
from pykeepass.entry import Entry
from pykeepass.group import Group

from .entry import KeepassEntryResource


class KeepassEntryProps(HomelabBaseModel):
    username: str
    password: str
    hostname: HttpUrl
    urls: list[HttpUrl]
    apps: list[str]


class KeepassProviderProps(HomelabRootModel[dict[str, KeepassEntryProps]]):
    @classmethod
    @contextmanager
    def open(cls) -> Iterator[tuple[PyKeePass, Group]]:
        filename = os.environ.get("KEEPASS_DATABASE")
        if filename:
            keepass = PyKeePass(
                filename,
                password=os.environ.get("KEEPASS_PASSWORD"),
                keyfile=os.environ.get("KEEPASS_KEYFILE"),
            )
            try:
                group = keepass.find_groups(
                    uuid=uuid.UUID(hex=os.environ["KEEPASS_GROUP"]), first=True
                )
                assert isinstance(group, Group)
                yield (keepass, group)
            finally:
                keepass.save()


class KeepassProvider(ResourceProvider):
    RESOURCE_ID = "keepass"

    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        keepass_props = KeepassProviderProps(**props)
        with keepass_props.open() as (keepass, group):
            for title, data in keepass_props.root.items():
                keepass.add_entry(
                    destination_group=group,
                    title=title,
                    username=data.username,
                    password=data.password,
                    url=str(data.hostname),
                )
        return CreateResult(
            id_=self.RESOURCE_ID, outs=keepass_props.model_dump(mode="json")
        )


class KeepassResousrce(Resource, module="keepass", name="Keepass"):
    def __init__(
        self,
        keepasses: dict[str, KeepassEntryResource],
    ):
        super().__init__(
            KeepassProvider(),
            KeepassProvider.RESOURCE_ID,
            {name: keepass.to_props() for name, keepass in keepasses.items()},
            None,
        )
