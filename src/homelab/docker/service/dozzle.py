from homelab_config import config
from homelab_docker.model.service import Model as ServiceModel
from homelab_docker.resource.service import Args, Base, BuildOption

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


class Dozzle(Base[None]):
    def __init__(self, model: ServiceModel[None], *, args: Args) -> None:
        super().__init__(model, args=args)

        self.build_containers(
            options={
                None: BuildOption(
                    envs={
                        "DOZZLE_FILTER": "label=pulumi.stack={}".format(
                            config.PROJECT_STACK
                        ),
                    },
                )
            }
        )

        self.register_outputs({})
