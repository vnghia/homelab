from pathlib import PosixPath
from typing import ClassVar

from homelab_docker.pydantic.path import AbsolutePath
from pydantic import BaseModel, ConfigDict, PositiveInt


class Postgres(BaseModel):
    model_config = ConfigDict(strict=True)

    DATABASE_TYPE: ClassVar[str] = "postgres"
    DATABASE_VERSION: ClassVar[PositiveInt] = 17

    PGRUN_PATH: ClassVar[AbsolutePath] = PosixPath("/var/run/postgresql")
    PGDATA_PATH: ClassVar[AbsolutePath] = PosixPath("/var/lib/postgresql/data")
    PORT: ClassVar[PositiveInt] = 5432

    PASSWORD_LENGTH: ClassVar[PositiveInt] = 64

    image: str = DATABASE_TYPE
    versions: list[PositiveInt] = [17]

    user: str | None = None
    database: str | None = None
    network: str = "internal-bridge"

    @classmethod
    def get_short_name(cls, name: str) -> str:
        return "{}{}{}".format(
            cls.DATABASE_TYPE,
            "" if name == cls.DATABASE_TYPE else "-",
            "" if name == cls.DATABASE_TYPE else name,
        )

    @classmethod
    def get_short_name_version(cls, name: str, version: PositiveInt) -> str:
        return "{}-{}".format(cls.get_short_name(name), version)

    @classmethod
    def get_full_name(cls, service_name: str, name: str) -> str:
        return "{}-{}".format(service_name, cls.get_short_name(name))

    @classmethod
    def get_full_name_version(
        cls, service_name: str, name: str, version: PositiveInt
    ) -> str:
        return "{}-{}".format(cls.get_full_name(service_name, name), version)

    def get_image(self, version: PositiveInt) -> str:
        return "{}-{}".format(self.image, version)
