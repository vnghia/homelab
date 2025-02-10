from homelab_docker.model.container.model import (
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from .config.backup import BackupConfig
from .resource.barman import BarmanResource


class BackupService(ServiceResourceBase[BackupConfig]):
    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions | None,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        super().__init__(
            model, opts=opts, container_model_global_args=container_model_global_args
        )

        self.barman = BarmanResource(
            self.model.config.barman,
            opts=self.child_opts,
            container_model=self.model.containers[BarmanResource.RESOURCE_NAME],
            database_source_configs=self.DATABASE_SOURCE_CONFIGS,
            volume_resource=self.container_model_global_args.docker_resource.volume,
        )

        self.build_containers(
            options={
                BarmanResource.RESOURCE_NAME: ContainerModelBuildArgs(
                    files=self.barman.files
                )
            }
        )
