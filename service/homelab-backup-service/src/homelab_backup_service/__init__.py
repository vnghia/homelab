from homelab_dagu_service import DaguService
from homelab_docker.config.volume import VolumeConfig
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

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

        self.build_containers(options={})

        self.register_outputs({})
