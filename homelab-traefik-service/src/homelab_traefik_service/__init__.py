from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_network.resource.network import NetworkResource
from homelab_tailscale_service import TailscaleService
from pulumi import ResourceOptions

from .config import TraefikConfig
from .config.dynamic.http import TraefikHttpDynamicConfig
from .config.dynamic.service import TraefikDynamicServiceConfig
from .config.static import TraefikStaticConfig


class TraefikService(ServiceResourceBase[TraefikConfig]):
    def __init__(
        self,
        model: ServiceModel[TraefikConfig],
        *,
        opts: ResourceOptions | None,
        network_resource: NetworkResource,
        docker_resource_args: DockerResourceArgs,
        tailscale_service: TailscaleService,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.static = TraefikStaticConfig(
            network_resource=network_resource,
            traefik_service_model=self.model,
            tailscale_service=tailscale_service,
        )
        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "CF_ZONE_API_TOKEN": network_resource.token.read.value,
                        "CF_DNS_API_TOKEN": network_resource.token.write.value,
                    },
                    files=[
                        self.static.build_resource(
                            opts=self.child_opts,
                            volume_resource=self.docker_resource_args.volume,
                        )
                    ],
                )
            }
        )

        self.dashboard = TraefikHttpDynamicConfig(
            name="{}-dashboard".format(self.name()),
            public=False,
            hostname="system",
            prefix=self.static.service_config.path,
            service=TraefikDynamicServiceConfig("api@internal"),
        ).build_resource(
            "dashboard",
            opts=self.child_opts,
            volume_resource=self.docker_resource_args.volume,
            containers=self.CONTAINERS,
            static_config=self.static,
        )

        self.register_outputs({})
