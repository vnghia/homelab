from enum import StrEnum, auto

from pydantic import PositiveInt


class DatabaseType(StrEnum):
    POSTGRES = auto()
    REDIS = auto()
    SQLITE = auto()
    MYSQL = auto()
    VALKEY = auto()

    def get_key(self, name: str | None) -> str | None:
        return None if name == self.value else name

    def get_short_name(self, name: str | None) -> str:
        value = self.value
        return "{}-{}".format(value, name) if name else value

    def get_short_name_version(self, name: str | None, version: PositiveInt) -> str:
        return "{}-{}".format(self.get_short_name(name), version)

    def get_full_name(self, service_name: str, name: str | None) -> str:
        return "{}-{}".format(service_name, self.get_short_name(name))

    def get_full_name_initdb(self, service_name: str, name: str | None) -> str:
        return "{}-initdb".format(self.get_full_name(service_name, name))

    def get_full_name_version(
        self, service_name: str, name: str | None, version: PositiveInt
    ) -> str:
        return "{}-{}".format(self.get_full_name(service_name, name), version)

    def get_full_name_version_tmp(
        self, service_name: str, name: str | None, version: PositiveInt
    ) -> str:
        return "{}-{}-tmp".format(self.get_full_name(service_name, name), version)

    def get_full_name_version_backup(
        self, service_name: str, name: str | None, version: PositiveInt
    ) -> str:
        return "{}-{}-backup".format(self.get_full_name(service_name, name), version)
