from homelab_config import Config
from homelab_docker.model.container.model import (
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_network.config.network import NetworkConfig
from homelab_network.resource.token import TokenResource
from pulumi import ResourceOptions

from homelab.docker.service.tailscale import TailscaleService
from homelab.docker.service.traefik.config.static import TraefikStaticConfig

from .config import TraefikConfig


class TraefikService(ServiceResourceBase[TraefikConfig]):
    def __init__(
        self,
        model: ServiceModel[TraefikConfig],
        *,
        opts: ResourceOptions | None,
        network_config: NetworkConfig,
        container_model_global_args: ContainerModelGlobalArgs,
        tailscale_service: TailscaleService,
    ) -> None:
        super().__init__(
            model, opts=opts, container_model_global_args=container_model_global_args
        )

        self.token = TokenResource(
            Config.get_name(None), network_config, opts=self.child_opts
        )
        self.static = TraefikStaticConfig(
            traefik_service_model=self.model, tailscale_service=tailscale_service
        )
        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "CF_ZONE_API_TOKEN": self.token.read.value,
                        "CF_DNS_API_TOKEN": self.token.write.value,
                    },
                    files=[
                        self.static.build_resource(
                            opts=self.child_opts,
                            volume_resource=container_model_global_args.docker_resource.volume,
                        )
                    ],
                )
            }
        )

        self.register_outputs({})


# class Traefik(Base):
#     def __init__(
#         self,
#         resource: Resource,
#         tailscale: Tailscale,
#         opts: ResourceOptions | None,
#     ) -> None:
#         super().__init__(resource=resource, opts=opts)

#         self.token = Token(opts=self.child_opts)
#         self.static = Static(self.config(), tailscale)

#         self.build_containers(
#             options={
#                 None: BuildOption(
#                     opts=ResourceOptions(delete_before_replace=True),
#                     envs={
#                         "CF_ZONE_API_TOKEN": self.token.read.value,
#                         "CF_DNS_API_TOKEN": self.token.write.value,
#                     },
#                     files=[
#                         self.static.build_resource(self.resource, opts=self.child_opts)
#                     ],
#                 )
#             }
#         )

#         self.dashboard = HttpDynamic(
#             name="{}-dashboard".format(self.name()),
#             public=False,
#             hostname="system",
#             prefix=self.static.service_config.path,
#             service="api@internal",
#         ).build_resource(
#             "dashboard", resource=resource, traefik=self.static, opts=self.child_opts
#         )
