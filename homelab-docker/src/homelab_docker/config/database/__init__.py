from pydantic import BaseModel, field_validator

from homelab_docker.model.database.postgres import PostgresDatabaseModel


class DatabaseConfig(BaseModel):
    postgres: dict[str | None, PostgresDatabaseModel] = {}

    @field_validator("postgres", mode="after")
    def set_postgres_none_key(
        cls, postgres: dict[str | None, PostgresDatabaseModel]
    ) -> dict[str | None, PostgresDatabaseModel]:
        return {
            PostgresDatabaseModel.get_key(name): model
            for name, model in postgres.items()
        }
