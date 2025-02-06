from homelab_config import Config
from homelab_docker.model.container import (
    ContainerModelBuildArgs,
    ContainerModelGlobalArgs,
)
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

# class Dozzle(Base):
#     def __init__(
#         self,
#         resource: Resource,
#         traefik: Static,
#         opts: ResourceOptions | None,
#     ) -> None:
#         super().__init__(resource=resource, opts=opts)

#         self.build_containers(
#             options={
#                 None: BuildOption(
#                     envs={
#                         "DOZZLE_FILTER": "label=pulumi.stack={}".format(
#                             config.PROJECT_STACK
#                         ),
#                     },
#                 )
#             }
#         )

#         self.prefix = self.config().container.envs["DOZZLE_BASE"].to_str()

#         self.traefik = HttpDynamic(
#             name=self.name(),
#             public=False,
#             hostname="system",
#             prefix=self.prefix,
#             service=int(self.config().container.envs["DOZZLE_ADDR"].to_str()[1:]),
#         ).build_resource(
#             "traefik", resource=resource, traefik=traefik, opts=self.child_opts
#         )
#         self.traefik_redirect = HttpDynamic(
#             name="{}-redirect".format(self.name()),
#             public=False,
#             hostname="system",
#             service=self.name(),
#             middlewares=[
#                 Middleware(
#                     name="{}-redirect".format(self.name()),
#                     data={"addPrefix": {"prefix": self.prefix}},
#                 )
#             ],
#         ).build_resource(
#             "traefik-redirect", resource=resource, traefik=traefik, opts=self.child_opts
#         )


class Dozzle(ServiceResourceBase[None]):
    def __init__(
        self,
        model: ServiceModel[None],
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
                    envs={
                        "DOZZLE_FILTER": "label=pulumi.stack={}".format(
                            Config.PROJECT_STACK
                        ),
                    },
                )
            }
        )

        self.register_outputs({})
