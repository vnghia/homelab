from homelab_config import Config
from homelab_docker.model.container import (
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.middleware import (
    TraefikDynamicMiddlewareConfig,
    TraefikDynamicMiddlewareFullConfig,
)
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from homelab_traefik_service.config.static import TraefikStaticConfig
from pulumi import ResourceOptions


class DozzleService(ServiceResourceBase[None]):
    def __init__(
        self,
        model: ServiceModel[None],
        *,
        opts: ResourceOptions | None,
        container_model_global_args: ContainerModelGlobalArgs,
        traefik_static_config: TraefikStaticConfig,
    ) -> None:
        super().__init__(
            model, opts=opts, container_model_global_args=container_model_global_args
        )

        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    envs={
                        "DOZZLE_FILTER": "label=pulumi.stack={}".format(
                            Config.PROJECT_STACK
                        ),
                    },
                )
            }
        )

        self.prefix = self.model.container.envs["DOZZLE_BASE"].to_str()

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=False,
            hostname="system",
            prefix=self.prefix,
            service=TraefikDynamicServiceConfig(
                int(self.model.container.envs["DOZZLE_ADDR"].to_str()[1:])
            ),
        ).build_resource(
            "traefik",
            opts=self.child_opts,
            volume_resource=container_model_global_args.docker_resource.volume,
            containers=self.CONTAINERS,
            static_config=traefik_static_config,
        )
        self.traefik_redirect = TraefikHttpDynamicConfig(
            name="{}-redirect".format(self.name()),
            public=False,
            hostname="system",
            service=TraefikDynamicServiceConfig(self.name()),
            middlewares=[
                TraefikDynamicMiddlewareConfig(
                    TraefikDynamicMiddlewareFullConfig(
                        name="{}-redirect".format(self.name()),
                        data={"addPrefix": {"prefix": self.prefix}},
                    )
                )
            ],
        ).build_resource(
            "traefik-redirect",
            opts=self.child_opts,
            volume_resource=container_model_global_args.docker_resource.volume,
            containers=self.CONTAINERS,
            static_config=traefik_static_config,
        )

        self.register_outputs({})
