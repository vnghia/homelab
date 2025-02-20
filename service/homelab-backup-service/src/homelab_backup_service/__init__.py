from homelab_backup.config import BackupConfig
from homelab_barman_service import BarmanService
from homelab_dagu_service import DaguService
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_restic_service import ResticService
from pulumi import ResourceOptions


class BackupService(ServiceResourceBase[BackupConfig]):
    def __init__(
        self,
        model: ServiceModel[BackupConfig],
        *,
        opts: ResourceOptions | None,
        dagu_service: DaguService,
        barman_service: BarmanService,
        restic_service: ResticService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(options={})

        self.register_outputs({})
