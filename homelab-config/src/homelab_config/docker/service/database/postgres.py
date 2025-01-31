from pathlib import PosixPath
from typing import ClassVar

from homelab_docker.pydantic.path import AbsolutePath
from pydantic import BaseModel, ConfigDict, PositiveInt


class Postgres(BaseModel):
    model_config = ConfigDict(strict=True)

    DATABASE_TYPE: ClassVar[str] = "postgres"

    PGRUN_PATH: ClassVar[AbsolutePath] = PosixPath("/var/run/postgresql")
    PGDATA_PATH: ClassVar[AbsolutePath] = PosixPath("/var/lib/postgresql/data")

    PASSWORD_LENGTH: ClassVar[PositiveInt] = 64

    image: str = DATABASE_TYPE
    user: str | None = None
    database: str | None = None
    network: str = "internal-bridge"

    @classmethod
    def get_short_name(cls, service_name: str, name: str) -> str:
        return "{}{}{}".format(
            cls.DATABASE_TYPE,
            "" if name == service_name else "-",
            "" if name == service_name else name,
        )

    @classmethod
    def get_full_name(cls, service_name: str, name: str) -> str:
        return "{}-{}".format(service_name, cls.get_short_name(service_name, name))
