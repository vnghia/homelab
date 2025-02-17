from homelab_dagu_service import DaguService
from homelab_docker.config.volume import VolumeConfig
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from homelab_backup_service.resource.restic import ResticResource

from .config import BackupConfig


class BackupService(ServiceResourceBase[BackupConfig]):
    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions | None,
        volume_config: VolumeConfig,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.restic = ResticResource(
            self.model,
            opts=self.child_opts,
            service_name=self.name(),
            volume_config=volume_config,
            dagu_service=dagu_service,
            docker_resource_args=self.docker_resource_args,
            service_resource_args=self.args,
        )

        self.build_containers(options={})

        self.register_outputs({})
