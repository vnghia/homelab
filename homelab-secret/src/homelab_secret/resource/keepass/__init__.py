import os
from contextlib import contextmanager
from typing import Any, Iterator, Self
from uuid import UUID

import pulumi
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

    @classmethod
    def from_entry(cls, entry: Entry) -> Self:
        return cls.model_validate(
            {
                "username": entry.username,
                "password": entry.password,
                "hostname": entry.url,
                "urls": [],
                "apps": [],
            }
        )


class KeepassProviderProps(HomelabBaseModel):
    entries: dict[str, KeepassEntryProps]
    entry_ids: dict[str, UUID] = {}


class Keepass:
    def __init__(self, filename: str, props: KeepassProviderProps) -> None:
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

        self.props = props

    def save(self) -> None:
        self.keepass.save()

    def find_entry(self, title: str) -> Entry | None:
        entry_id = self.props.entry_ids.get(title)
        if entry_id:
            entry = self.keepass.find_entries(uuid=entry_id, first=True)
            if entry:
                assert isinstance(entry, Entry)
                return entry
            else:
                pulumi.warn(
                    "Could not find entry with title {} and id {}".format(
                        title, entry_id
                    )
                )
                self.props.entry_ids.pop(title)

        path = list(self.group.path) + [title]
        entry = self.keepass.find_entries(path=path)
        if entry:
            assert isinstance(entry, Entry)
            self.props.entry_ids[title] = entry.uuid
            return entry
        else:
            return None

    def add_entry(self, title: str, props: KeepassEntryProps) -> None:
        entry = self.keepass.add_entry(
            destination_group=self.group,
            title=title,
            username=props.username,
            password=props.password,
            url=str(props.hostname),
        )
        self.props.entry_ids[title] = entry.uuid

    def update_entry(self, entry: Entry, props: KeepassEntryProps) -> None:
        entry.username = props.username
        entry.password = props.password
        entry.url = str(props.hostname)

    def upsert_props(self) -> None:
        for title, entry_props in self.props.entries.items():
            entry = self.find_entry(title)
            if not entry:
                self.add_entry(title=title, props=entry_props)
            elif KeepassEntryProps.from_entry(entry) != entry_props:
                self.update_entry(entry, entry_props)
        for entry in self.group.entries:
            entry_id = self.props.entry_ids.get(str(entry.title))
            if entry.uuid != entry_id:
                self.keepass.delete_entry(entry)

    @classmethod
    @contextmanager
    def open(cls, props: KeepassProviderProps) -> Iterator[Self]:
        filename = os.environ.get("KEEPASS_DATABASE")
        if filename:
            keepass = cls(filename, props)
            try:
                yield keepass
            finally:
                keepass.save()


class KeepassProvider(ResourceProvider):
    RESOURCE_ID = "keepass"

    serialize_as_secret_always = False

    def create(self, props: dict[str, Any]) -> CreateResult:
        keepass_props = KeepassProviderProps(**props)
        with Keepass.open(keepass_props) as keepass:
            keepass.upsert_props()
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
