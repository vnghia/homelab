from __future__ import annotations

import os
import re
from contextlib import contextmanager
from typing import Any, ClassVar, Iterator, Self
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
from pydantic import (
    HttpUrl,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)
from pykeepass import PyKeePass
from pykeepass.entry import Entry
from pykeepass.group import Group

from .entry import KeepassEntryResource


class KeepassEntryProps(HomelabBaseModel):
    URL_PREFIX: ClassVar[str] = "KP2A_URL_"
    URL_PATTERN: ClassVar[re.Pattern[str]] = re.compile("{}(\\d+)".format(URL_PREFIX))

    APP_PREFIX: ClassVar[str] = "AndroidApp"
    APP_PATTERN: ClassVar[re.Pattern[str]] = re.compile("{}(\\d+)".format(APP_PREFIX))

    username: str
    password: str
    hostname: HttpUrl
    urls: list[HttpUrl]
    apps: list[str]

    @field_validator("username", "password", "hostname", mode="wrap")
    @classmethod
    def ignore_pulumi_unknown(
        cls, data: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> KeepassEntryProps:
        if isinstance(data, pulumi.output.Unknown):
            pulumi.log.warn(
                "Pulumi unknown output encountered: {}. Validated data: {}".format(
                    data, info.data
                )
            )
            return KeepassEntryProps(
                username="",
                password="",
                hostname=HttpUrl("http://example.com"),
                urls=[],
                apps=[],
            )
        else:
            return handler(data)  # type: ignore[no-any-return]

    @classmethod
    def from_entry(cls, entry: Entry) -> Self:
        urls = {
            int(match[1]): HttpUrl(str(v))
            for k, v in entry.custom_properties.items()
            if (match := cls.URL_PATTERN.match(str(k)))
        }
        apps = {
            int(match[1]): str(v)
            for k, v in entry.custom_properties.items()
            if (match := cls.APP_PATTERN.match(str(k)))
        }

        return cls.model_validate(
            {
                "username": entry.username,
                "password": entry.password,
                "hostname": entry.url,
                "urls": [x[1] for x in sorted(urls.items(), key=lambda x: x[0])],
                "apps": [x[1] for x in sorted(apps.items(), key=lambda x: x[0])],
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

        for index, url in enumerate(props.urls):
            entry.set_custom_property(props.URL_PREFIX + str(index + 1), str(url))
        for index, app in enumerate(props.apps):
            entry.set_custom_property(props.APP_PREFIX + str(index + 1), str(app))

        self.props.entry_ids[title] = entry.uuid

    def update_entry(self, entry: Entry, props: KeepassEntryProps) -> None:
        entry.username = props.username
        entry.password = props.password
        entry.url = str(props.hostname)

        delete_keys = []
        for key in entry.custom_properties.keys():
            key = str(key)
            match = props.URL_PATTERN.match(key)
            if match:
                index = int(match[1])
                if index > len(props.urls):
                    delete_keys.append(key)
            match = props.APP_PATTERN.match(key)
            if match:
                index = int(match[1])
                if index > len(props.urls):
                    delete_keys.append(key)
        for key in delete_keys:
            entry.delete_custom_property(key)

        for index, url in enumerate(props.urls):
            entry.set_custom_property(props.URL_PREFIX + str(index + 1), str(url))
        for index, app in enumerate(props.apps):
            entry.set_custom_property(props.APP_PREFIX + str(index + 1), str(app))

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

    def read_props(self) -> KeepassProviderProps:
        for title in self.props.entries.keys():
            self.find_entry(title)
        return self.props

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

    def diff(self, _id: str, olds: dict[str, Any], news: dict[str, Any]) -> DiffResult:
        keepass_olds = KeepassProviderProps(**olds)
        keepass_news = KeepassProviderProps(**news)
        return DiffResult(
            changes=(keepass_olds.entry_ids.keys() != keepass_news.entries.keys())
            or (keepass_olds.entries != keepass_news.entries)
        )

    def update(
        self, _id: str, olds: dict[str, Any], news: dict[str, Any]
    ) -> UpdateResult:
        keepass_props = KeepassProviderProps(**news)
        with Keepass.open(keepass_props) as keepass:
            keepass.upsert_props()
        return UpdateResult(outs=keepass_props.model_dump(mode="json"))

    def read(self, id_: str, props: dict[str, Any]) -> ReadResult:
        keepass_props = KeepassProviderProps(**props)
        with Keepass.open(keepass_props) as keepass:
            ReadResult(id_=id_, outs=keepass.read_props().model_dump(mode="json"))
        return ReadResult(id_=id_, outs=keepass_props.model_dump(mode="json"))


class KeepassResource(Resource, module="keepass", name="Keepass"):
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
