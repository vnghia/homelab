import homelab_config as config
from pulumi import ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.service.traefik import Traefik
from homelab.docker.service.traefik.config.dynamic.http import HttpDynamic
from homelab.docker.service.traefik.config.dynamic.middleware import Middleware


class Dozzle(Base):
    def __init__(
        self,
        resource: Resource,
        traefik: Traefik,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.build_containers(
            options={
                None: BuildOption(
                    envs={
                        "DOZZLE_FILTER": "label=pulumi.stack={}".format(
                            config.constant.PROJECT_STACK
                        ),
                    },
                )
            }
        )

        self.prefix = self.config().container.envs["DOZZLE_BASE"].to_str()
        self.port = int(self.config().container.envs["DOZZLE_ADDR"].to_str()[1:])

        self.traefik = HttpDynamic(
            name=self.name(),
            public=False,
            hostname="system",
            prefix=self.prefix,
            port=self.port,
        ).build_resource(
            "traefik", resource=resource, traefik=traefik, opts=self.child_opts
        )
        self.traefik_redirect = HttpDynamic(
            name="{}-redirect".format(self.name()),
            public=False,
            hostname="system",
            container=self.name(),
            port=self.port,
            middlewares=[
                Middleware(
                    name="{}-redirect".format(self.name()),
                    data={"addPrefix": {"prefix": self.prefix}},
                )
            ],
        ).build_resource(
            "traefik-redirect", resource=resource, traefik=traefik, opts=self.child_opts
        )
