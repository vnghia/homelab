from pulumi import ResourceOptions

from homelab import common
from homelab.docker.resource import Resource
from homelab.docker.service.base import Base, BuildOption


class Dozzle(Base):
    def __init__(
        self,
        resource: Resource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.build_containers(
            options={
                None: BuildOption(
                    envs={
                        "DOZZLE_FILTER": f"label=pulumi.stack={common.constant.PROJECT_STACK}",
                    },
                )
            }
        )
