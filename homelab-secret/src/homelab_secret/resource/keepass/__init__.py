import os
from contextlib import contextmanager
from typing import Any, Iterator, Self
from uuid import UUID

from homelab_pydantic import HomelabBaseModel
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


class Keepass:
    def __init__(self, filename: str) -> None:
        self.keepass = PyKeePass(
            filename,
            password=os.environ.get("KEEPASS_PASSWORD"),
            keyfile=os.environ.get("KEEPASS_KEYFILE"),
        )

        group = self.keepass.find_groups(
            uuid=UUID(hex=os.environ["KEEPASS_GROUP"]), first=True
        )
        assert isinstance(group, Group)
        self.group = group

    def save(self) -> None:
        self.keepass.save()

    def find_entry(self, title: str) -> KeepassEntryProps | None:
        path = list(self.group.path) + [title]
        entry = self.keepass.find_entries(path=path)
        if entry:
            assert isinstance(entry, Entry)
            return KeepassEntryProps.model_validate(
                {
                    "username": entry.username,
                    "password": entry.password,
                    "hostname": entry.url,
                    "urls": [],
                    "apps": [],
                }
            )
        else:
            return None

    def add_entry(self, title: str, props: KeepassEntryProps) -> None:
        self.keepass.add_entry(
            destination_group=self.group,
            title=title,
            username=props.username,
            password=props.password,
            url=str(props.hostname),
        )

    @classmethod
    @contextmanager
    def open(cls) -> Iterator[Self]:
        filename = os.environ.get("KEEPASS_DATABASE")
        if filename:
            keepass = cls(filename)
            try:
                yield keepass
            finally:
                keepass.save()


class KeepassProviderProps(HomelabBaseModel):
    entries: dict[str, KeepassEntryProps]


class KeepassProvider(ResourceProvider):
    RESOURCE_ID = "keepass"

    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        keepass_props = KeepassProviderProps(**props)
        with Keepass.open() as keepass:
            for title, entry_props in keepass_props.entries.items():
                entry = keepass.find_entry(title)
                if not entry:
                    keepass.add_entry(title=title, props=entry_props)
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
            {
                "entries": {
                    name: keepass.to_props() for name, keepass in keepasses.items()
                }
            },
            None,
        )
