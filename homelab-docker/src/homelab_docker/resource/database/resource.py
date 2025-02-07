import pulumi_docker as docker
from pulumi import ComponentResource, ResourceOptions

from homelab_docker.config.database import DatabaseConfig
from homelab_docker.config.database.source import DatabaseSourceConfig
from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.resource.database.postgres import PostgresDatabaseResource


class DatabaseResource(ComponentResource):
    RESOURCE_NAME = "database"

    def __init__(
        self,
        model: DatabaseConfig,
        *,
        opts: ResourceOptions,
        service_name: str,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, service_name, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.postgres = {
            name: PostgresDatabaseResource(
                model,
                opts=self.child_opts,
                service_name=service_name,
                name=name,
                container_model_global_args=container_model_global_args,
            )
            for name, model in model.postgres.items()
        }

    @property
    def containers(self) -> dict[str, docker.Container]:
        return {
            resource.get_short_name_version(version): container
            for resource in self.postgres.values()
            for version, container in resource.containers.items()
        }

    @property
    def source_config(self) -> DatabaseSourceConfig:
        return DatabaseSourceConfig(
            {
                name: {
                    version: resource.to_source_model(version)
                    for version in resource.model.versions
                }
                for name, resource in self.postgres.items()
            }
        )
