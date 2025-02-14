from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from homelab_traefik_service.config.static import TraefikStaticConfig
from pulumi import ResourceOptions


class MemosService(ServiceResourceBase[None]):
    def __init__(
        self,
        model: ServiceModel[None],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
        traefik_static_config: TraefikStaticConfig,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.build_containers(options={})

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=True,
            service=TraefikDynamicServiceConfig(
                int(self.model.container.envs["MEMOS_PORT"].to_str())
            ),
        ).build_resource(
            "traefik",
            opts=self.child_opts,
            volume_resource=self.docker_resource_args.volume,
            containers=self.CONTAINERS,
            static_config=traefik_static_config,
        )

        self.register_outputs({})
