from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_pydantic.model import HomelabBaseModel
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from pulumi import ResourceOptions


class ExtraConfig(HomelabBaseModel):
    traefik: TraefikHttpDynamicConfig | None = None


class ExtraService(ServiceWithConfigResourceBase[ExtraConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[ExtraConfig],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(options={})

        if self.config.traefik:
            self.traefik = self.config.traefik.build_resource(
                None,
                opts=self.child_opts,
                main_service=self,
                traefik_service=traefik_service,
            )

        self.register_outputs({})
