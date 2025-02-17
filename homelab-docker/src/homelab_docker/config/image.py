from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt, field_validator

from ..model.image import RemoteImageModel
from ..model.image.build import BuildImageModel


class ImageConfig(HomelabBaseModel):
    remote: dict[str, RemoteImageModel]
    build: dict[str, BuildImageModel]
    postgres: dict[str | None, dict[PositiveInt, RemoteImageModel]]

    @field_validator("postgres", mode="after")
    def set_postgres_none_key(
        cls, postgres: dict[str | None, dict[PositiveInt, RemoteImageModel]]
    ) -> dict[str | None, dict[PositiveInt, RemoteImageModel]]:
        from ..model.database.postgres import PostgresDatabaseModel

        return {
            PostgresDatabaseModel.get_key(name): model
            for name, model in postgres.items()
        }
