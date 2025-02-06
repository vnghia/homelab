# from pulumi import ResourceOptions

# from homelab.docker.resource import Resource
# from homelab.docker.service.base import Base, BuildOption
# from homelab.docker.service.tailscale import Tailscale
# from homelab.docker.service.traefik.config.dynamic.http import HttpDynamic
# from homelab.docker.service.traefik.config.static import Static
# from homelab.network.dns.token import Token

from homelab_docker.interpolation.container_volume_path import ContainerVolumePath
from homelab_docker.model.container import (
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.pydantic.path import RelativePath
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class TraefikAcmeConfig(BaseModel):
    server: HttpUrl
    email: str
    storage: ContainerVolumePath


class TraefikProviderConfig(BaseModel):
    file: RelativePath


class TraefikEntrypointConfig(BaseModel):
    public_http: str = Field(alias="public-http")
    private_http: str = Field(alias="private-http")
    public_https: str = Field(alias="public-https")
    private_https: str = Field(alias="private-https")


class TraefikConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    path: str
    acme: TraefikAcmeConfig
    provider: TraefikProviderConfig
    entrypoint: TraefikEntrypointConfig


class Traefik(ServiceResourceBase[TraefikConfig]):
    def __init__(
        self,
        model: ServiceModel[TraefikConfig],
        *,
        opts: ResourceOptions | None,
        container_model_global_args: ContainerModelGlobalArgs,
    ) -> None:
        super().__init__(
            model, opts=opts, container_model_global_args=container_model_global_args
        )

        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={},
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
