from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from pulumi import ResourceOptions


class MemosService(ServiceResourceBase):
    PORT_ENV = "MEMOS_PORT"

    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(options={})

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=True,
            service=TraefikDynamicServiceConfig(
                int(self.model[None].envs[self.PORT_ENV].extract_str(self.model[None]))
            ),
        ).build_resource(
            None,
            opts=self.child_opts,
            main_service=self,
            traefik_service=traefik_service,
        )

        self.register_outputs({})
