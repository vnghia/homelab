from homelab_pydantic import HomelabBaseModel
from pydantic import field_validator

from ...model.database.postgres import PostgresDatabaseModel


class DatabaseConfig(HomelabBaseModel):
    postgres: dict[str | None, PostgresDatabaseModel] = {}

    @field_validator("postgres", mode="after")
    def set_postgres_none_key(
        cls, postgres: dict[str | None, PostgresDatabaseModel]
    ) -> dict[str | None, PostgresDatabaseModel]:
        return {
            PostgresDatabaseModel.get_key(name): model
            for name, model in postgres.items()
        }
