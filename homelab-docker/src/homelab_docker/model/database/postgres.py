from pathlib import PosixPath
from typing import ClassVar

from pydantic import BaseModel, PositiveInt

from homelab_docker.pydantic import AbsolutePath

from ..container.network import ContainerNetworkConfig


class PostgresDatabaseModel(BaseModel):
    DATABASE_TYPE: ClassVar[str] = "postgres"
    DATABASE_VERSION: ClassVar[PositiveInt] = 17

    PGRUN_PATH: ClassVar[AbsolutePath] = PosixPath("/var/run/postgresql")
    PGDATA_PATH: ClassVar[AbsolutePath] = PosixPath("/var/lib/postgresql/data")
    PORT: ClassVar[PositiveInt] = 5432

    PASSWORD_LENGTH: ClassVar[PositiveInt] = 64

    image: str = DATABASE_TYPE
    versions: list[PositiveInt] = [DATABASE_VERSION]

    username: str | None = None
    database: str | None = None

    network: ContainerNetworkConfig = ContainerNetworkConfig()

    @classmethod
    def get_key(cls, name: str | None) -> str | None:
        return None if name == cls.DATABASE_TYPE else name

    @classmethod
    def get_short_name(cls, name: str | None) -> str:
        if name:
            return "{}-{}".format(cls.DATABASE_TYPE, name)
        else:
            return cls.DATABASE_TYPE

    @classmethod
    def get_short_name_version(cls, name: str | None, version: PositiveInt) -> str:
        return "{}-{}".format(cls.get_short_name(name), version)

    @classmethod
    def get_full_name(cls, service_name: str, name: str | None) -> str:
        return "{}-{}".format(service_name, cls.get_short_name(name))

    @classmethod
    def get_full_name_version(
        cls, service_name: str, name: str | None, version: PositiveInt
    ) -> str:
        return "{}-{}".format(cls.get_full_name(service_name, name), version)
