from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class Postgres(BaseModel):
    model_config = ConfigDict(strict=True)
    DATABASE_TYPE: ClassVar[str] = "postgres"

    image: str = DATABASE_TYPE
