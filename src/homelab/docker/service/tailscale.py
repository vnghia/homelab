import pulumi_tailscale as tailscale
from pulumi import ResourceOptions

from homelab.docker.image import Image
from homelab.docker.service.base import Base
from homelab.docker.volume import Volume


class Tailscale(Base):
    RESOURCE_NAME = "tailscale"

    def __init__(
        self, image: Image, volume: Volume, opts: ResourceOptions | None
    ) -> None:
        super().__init__(
            image=image, volume=volume, resource_name=self.RESOURCE_NAME, opts=opts
        )

        self.build_containers(
            envs={
                self.resource_name: {
                    "TS_AUTHKEY": self.build_authkey().key,
                }
            }
        )

        self.register_outputs(self.container_outputs())

    def build_authkey(self) -> tailscale.TailnetKey:
        self.authkey = tailscale.TailnetKey(
            "tailscale",
            opts=self.child_opts,
            ephemeral=False,
            expiry=5 * 60,
            preauthorized=True,
            reusable=False,
        )
        return self.authkey
