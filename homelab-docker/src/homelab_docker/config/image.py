from pydantic import BaseModel, PositiveInt, field_validator

from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.image import RemoteImageModel
from homelab_docker.model.platform import Platform


class ImageConfig(BaseModel):
    platform: Platform
    remote: dict[str, RemoteImageModel]
    postgres: dict[str | None, dict[PositiveInt, RemoteImageModel]]

    @field_validator("postgres", mode="after")
    def set_postgres_none_key(
        cls, postgres: dict[str | None, dict[PositiveInt, RemoteImageModel]]
    ) -> dict[str | None, dict[PositiveInt, RemoteImageModel]]:
        return {
            PostgresDatabaseModel.get_key(name): model
            for name, model in postgres.items()
        }
