from pulumi import ComponentResource, ResourceOptions

from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.model.database import DatabaseModel
from homelab_docker.resource.database.postgres import PostgresDatabaseResource


class DatabaseResource(ComponentResource):
    RESOURCE_NAME = "database"

    def __init__(
        self,
        model: DatabaseModel,
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
