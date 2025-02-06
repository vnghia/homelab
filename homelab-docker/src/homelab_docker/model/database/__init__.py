from pydantic import BaseModel, field_validator

from .postgres import PostgresDatabaseModel


class DatabaseModel(BaseModel):
    postgres: dict[str | None, PostgresDatabaseModel] = {}

    @field_validator("postgres", mode="after")
    def set_postgres_none_key(
        cls, postgres: dict[str | None, PostgresDatabaseModel]
    ) -> dict[str | None, PostgresDatabaseModel]:
        return {
            None if name == PostgresDatabaseModel.DATABASE_TYPE else name: model
            for name, model in postgres.items()
        }
