from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from .config import DozzleConfig


class DozzleService(ServiceWithConfigResourceBase[DozzleConfig]):
    BASE_ENV = "DOZZLE_BASE"
    ADDR_ENV = "DOZZLE_ADDR"

    def __init__(
        self,
        model: ServiceWithConfigModel[DozzleConfig],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(options={})

        self.traefik = self.config.traefik.build_resources(
            opts=self.child_opts, main_service=self, traefik_service=traefik_service
        )

        self.register_outputs({})
