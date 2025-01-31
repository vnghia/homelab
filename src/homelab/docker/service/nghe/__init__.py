import binascii

import pulumi_random as random
from pulumi import ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.service.nghe.config import Config
from homelab.docker.service.traefik import Traefik
from homelab.docker.service.traefik.config.dynamic.http import HttpDynamic


class Nghe(Base):
    KEY_LENGTH = 16

    def __init__(
        self,
        resource: Resource,
        traefik: Traefik,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.service_config = self.config().config(Config)

        self.key = random.RandomPassword(
            "key", opts=self.child_opts, length=self.KEY_LENGTH, special=False
        ).result
        self.build_containers(
            options={
                None: BuildOption(
                    envs={
                        "NGHE_DATABASE__URL": self.postgres[None].get_url().apply(str),
                        "NGHE_DATABASE__KEY": self.key.apply(
                            lambda x: binascii.hexlify(x.encode()).decode("ascii")
                        ),
                        "NGHE_INTEGRATION__SPOTIFY__ID": self.service_config.spotify.id,
                        "NGHE_INTEGRATION__SPOTIFY__SECRET": self.service_config.spotify.secret,
                        "NGHE_INTEGRATION__LASTFM__KEY": self.service_config.lastfm.key,
                    },
                    opts=ResourceOptions(depends_on=[self.postgres[None].container]),
                )
            }
        )

        self.traefik = HttpDynamic(
            name=self.name(),
            public=True,
            port=int(self.config().container.envs["NGHE_SERVER__PORT"].to_str()),
        ).build_resource(
            "traefik", resource=resource, traefik=traefik, opts=self.child_opts
        )
