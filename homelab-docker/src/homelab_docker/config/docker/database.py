from typing import ClassVar, Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from homelab_pydantic.path import AbsolutePath
from pydantic import PositiveInt, model_validator

from ...model.database.type import DatabaseType
from ...model.docker.container import ContainerModel
from ...model.docker.image import RemoteImageModel
from ...model.service.database import (
    ServiceDatabaseInitScriptModel,
    ServiceDatabaseModel,
)


class DatabaseRemoteImageModel(RemoteImageModel):
    container: ContainerModel | None = None


class DatabaseTypeDirConfig(HomelabBaseModel):
    data: AbsolutePath
    tmp: AbsolutePath | None = None
    initdb: AbsolutePath | None = None


class DatabaseTypeBackupConfig(HomelabBaseModel):
    pass


class DatabaseTypeEnvConfig(HomelabBaseModel):
    DEFAULT_USERNAME: ClassVar[str] = "default"

    username: str | None = None
    password: str
    database: str
    data_dir: str

    superuser_password: str | None = None


class DatabaseTypeConfig(HomelabBaseModel):
    images: dict[str | None, dict[PositiveInt, DatabaseRemoteImageModel]]
    version: PositiveInt
    port: PositiveInt

    dir: DatabaseTypeDirConfig
    backup: DatabaseTypeBackupConfig | None = None
    scripts: list[ServiceDatabaseInitScriptModel] = []

    env: DatabaseTypeEnvConfig
    container: ContainerModel

    def get_versions(self, model: ServiceDatabaseModel) -> list[PositiveInt]:
        return model.versions or [self.version]


class DatabaseConfig(HomelabRootModel[dict[DatabaseType, DatabaseTypeConfig]]):
    root: dict[DatabaseType, DatabaseTypeConfig] = {}

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
