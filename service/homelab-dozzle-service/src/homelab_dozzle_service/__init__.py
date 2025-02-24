from homelab_config import Config
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.middleware import (
    TraefikDynamicMiddlewareConfig,
    TraefikDynamicMiddlewareFullConfig,
)
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from pulumi import ResourceOptions


class DozzleService(ServiceResourceBase):
    BASE_ENV = "DOZZLE_BASE"
    ADDR_ENV = "DOZZLE_ADDR"

    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

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

        self.prefix = self.model[None].envs[self.BASE_ENV].extract_str(self.model[None])

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=False,
            hostname="system",
            prefix=self.prefix,
            service=TraefikDynamicServiceConfig(
                int(
                    self.model[None]
                    .envs[self.ADDR_ENV]
                    .extract_str(self.model[None])[1:]
                )
            ),
        ).build_resource(None, opts=self.child_opts, traefik_service=traefik_service)
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
        ).build_resource(None, opts=self.child_opts, traefik_service=traefik_service)

        self.register_outputs({})
