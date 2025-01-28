from ipaddress import IPv4Address, IPv6Address

import pulumi
import pulumi_tailscale as tailscale
from pulumi import ResourceOptions

from homelab import common
from homelab.docker.image import Image
from homelab.docker.network import Network
from homelab.docker.service.base import Base, BuildOption
from homelab.docker.volume import Volume


class Tailscale(Base):
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
            opts=opts,
        )

        self.hostname = common.get_name(name=None, project=True, stack=True)
        self.build_containers(
            options={
                None: BuildOption(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "TS_AUTHKEY": self.build_authkey().key,
                        "TS_HOSTNAME": self.hostname,
                    },
                )
            }
        )

        self.device = tailscale.get_device_output(
            hostname=self.container.id.apply(lambda _: self.hostname)
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
