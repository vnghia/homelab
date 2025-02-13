from pydantic import BaseModel, PositiveInt, field_validator

from homelab_docker.model.build.model import BuildModel
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.image import RemoteImageModel


class ImageConfig(BaseModel):
    remote: dict[str, RemoteImageModel]
    build: dict[str, BuildModel]
    postgres: dict[str | None, dict[PositiveInt, RemoteImageModel]]

    @field_validator("postgres", mode="after")
    def set_postgres_none_key(
        cls, postgres: dict[str | None, dict[PositiveInt, RemoteImageModel]]
    ) -> dict[str | None, dict[PositiveInt, RemoteImageModel]]:
        return {
            PostgresDatabaseModel.get_key(name): model
            for name, model in postgres.items()
        }
