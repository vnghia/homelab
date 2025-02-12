from homelab_dagu_service import DaguService
from homelab_docker.model.container.model import ContainerModelGlobalArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_integration.config.s3 import S3IntegrationConfig
from pulumi import ResourceOptions

from .config.backup import BackupConfig
from .resource.barman import BarmanResource


class BackupService(ServiceResourceBase[BackupConfig]):
    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions | None,
        s3_integration_config: S3IntegrationConfig,
        dagu_service: DaguService,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        super().__init__(
            model, opts=opts, container_model_global_args=container_model_global_args
        )

        self.barman = BarmanResource(
            self.model,
            opts=self.child_opts,
            service_name=self.name(),
            dagu_service=dagu_service,
            database_source_configs=self.DATABASE_SOURCE_CONFIGS,
            container_model_global_args=self.container_model_global_args,
            containers=self.CONTAINERS,
        )
