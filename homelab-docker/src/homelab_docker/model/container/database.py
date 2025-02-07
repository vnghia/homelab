from pydantic import BaseModel, Field, PositiveInt, RootModel

from homelab_docker.config.database import DatabaseConfig


class ContainerPostgresDatabaseConfig(BaseModel):
    name: str | None = Field(alias="postgres")
    version: PositiveInt | None = None

    def to_container_name(
        self, service_name: str, database_config: DatabaseConfig
    ) -> str:
        model = database_config.postgres[self.name]
        version = self.version or model.versions[0]
        return model.get_full_name_version(service_name, self.name, version)


class ContainerDatabaseConfig(RootModel[ContainerPostgresDatabaseConfig]):
    def to_container_name(
        self, service_name: str, database_config: DatabaseConfig
    ) -> str:
        return self.root.to_container_name(service_name, database_config)
