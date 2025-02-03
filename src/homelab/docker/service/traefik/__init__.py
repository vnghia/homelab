from pulumi import ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.service.traefik.config.dynamic.http import HttpDynamic
from homelab.docker.service.traefik.config.static import Static
from homelab.network.dns.token import Token


class Traefik(Base):
    def __init__(
        self,
        resource: Resource,
        tailscale: Tailscale,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.token = Token(opts=self.child_opts)
        self.static = Static(self.config(), tailscale)

        self.build_containers(
            options={
                None: BuildOption(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "CF_ZONE_API_TOKEN": self.token.read.value,
                        "CF_DNS_API_TOKEN": self.token.write.value,
                    },
                    files=[
                        self.static.build_resource(self.resource, opts=self.child_opts)
                    ],
                )
            }
        )

        self.dashboard = HttpDynamic(
            name="{}-dashboard".format(self.name()),
            public=False,
            hostname="system",
            prefix=self.static.service_config.path,
            service="api@internal",
        ).build_resource(
            "dashboard", resource=resource, traefik=self.static, opts=self.child_opts
        )
