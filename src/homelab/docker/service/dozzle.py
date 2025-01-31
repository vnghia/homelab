from pulumi import ResourceOptions

from homelab import common
from homelab.docker.resource import Resource
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.service.traefik import Traefik
from homelab.docker.service.traefik.config.dynamic.http import HttpDynamic


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
                            common.constant.PROJECT_STACK
                        ),
                    },
                )
            }
        )

        self.traefik = HttpDynamic(
            name=self.name(),
            public=False,
            prefix=self.config().container.envs["DOZZLE_BASE"].to_str(),
            port=int(self.config().container.envs["DOZZLE_ADDR"].to_str()[1:]),
        ).build_resource(
            "traefik", resource=resource, traefik=traefik, opts=self.child_opts
        )
