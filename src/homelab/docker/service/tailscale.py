from ipaddress import IPv4Address, IPv6Address

import pulumi
import pulumi_tailscale as tailscale
from pulumi import InvokeOptions, ResourceOptions

from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.volume import Volume


class Tailscale(Base):
    RESOURCE_NAME = "tailscale"

    def __init__(
        self,
        network: Network,
        image: Image,
        volume: Volume,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(
            network=network,
            image=image,
            volume=volume,
            resource_name=self.RESOURCE_NAME,
            opts=opts,
        )

        self.build_containers(
            options={
                self.resource_name: BuildOption(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "TS_AUTHKEY": self.build_authkey().key,
                    },
                )
            }
        )

        self.device = tailscale.get_device_output(
            hostname=self.container.hostname, opts=InvokeOptions(parent=self.container)
        )
        self.ipv4 = self.device.apply(lambda x: IPv4Address(x.addresses[0]))
        self.ipv6 = self.device.apply(lambda x: IPv6Address(x.addresses[1]))

        outputs = self.container_outputs() | {
            "ipv4": self.ipv4.apply(str),
            "ipv6": self.ipv6.apply(str),
        }
        pulumi.export("tailscale-ipv4", outputs["ipv4"])
        pulumi.export("tailscale-ipv6", outputs["ipv6"])
        self.register_outputs(outputs)

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
