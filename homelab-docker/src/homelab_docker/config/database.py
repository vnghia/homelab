from __future__ import annotations

import typing
from typing import ClassVar, Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_pydantic.path import AbsolutePath
from pydantic import PositiveInt, model_validator

from ..model.container import ContainerModel
from ..model.database.type import DatabaseType
from ..model.image import RemoteImageModel

if typing.TYPE_CHECKING:
    from ..model.service.database import ServiceDatabaseModel


class DatabaseTypeEnvConfig(HomelabBaseModel):
    DEFAULT_USERNAME: ClassVar[str] = "default"

    username: str | None = None
    password: str
    database: str
    data_dir: str

    superuser_password: str | None = None


class DatabaseTypeConfig(HomelabBaseModel):
    images: dict[str | None, dict[PositiveInt, RemoteImageModel]]
    version: PositiveInt
    port: PositiveInt

    data_dir: AbsolutePath
    tmp_dir: AbsolutePath | None = None
    initdb_dir: AbsolutePath | None = None

    env: DatabaseTypeEnvConfig
    container: ContainerModel

    def get_versions(self, model: ServiceDatabaseModel) -> list[PositiveInt]:
        return model.versions or [self.version]


class DatabaseConfig(HomelabRootModel[dict[DatabaseType, DatabaseTypeConfig]]):
    @model_validator(mode="after")
    def set_images_none_key(self) -> Self:
        return self.model_construct(
            {
                type_: config.__replace__(
                    images={
                        type_.get_key(name): model
                        for name, model in config.images.items()
                    }
                )
                for type_, config in self.root.items()
            }
        )
