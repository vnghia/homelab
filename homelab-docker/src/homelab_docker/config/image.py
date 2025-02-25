from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt, field_validator

from ..model.database.type import DatabaseType
from ..model.image import RemoteImageModel
from ..model.image.build import BuildImageModel


class ImageConfig(HomelabBaseModel):
    remote: dict[str, RemoteImageModel]
    build: dict[str, BuildImageModel]
    database: dict[DatabaseType, dict[str | None, dict[PositiveInt, RemoteImageModel]]]

    @field_validator("database", mode="after")
    def set_database_none_key(
        cls,
        database: dict[
            DatabaseType, dict[str | None, dict[PositiveInt, RemoteImageModel]]
        ],
    ) -> dict[DatabaseType, dict[str | None, dict[PositiveInt, RemoteImageModel]]]:
        return {
            type_: {type_.get_key(name): model for name, model in config.items()}
            for type_, config in database.items()
        }
