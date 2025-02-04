from ipaddress import IPv4Address, IPv6Address

import pulumi
import pulumi_tailscale as tailscale
from homelab_config import config
from pulumi import InvokeOutputOptions, Output, ResourceOptions
from pydantic import IPvAnyAddress

from homelab.docker.resource import Resource
from homelab.docker.service.base import Base, BuildOption


class Tailscale(Base):
    def __init__(
        self,
        resource: Resource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(resource=resource, opts=opts)

        self.hostname = config.get_name(name=None, project=True, stack=True)
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
            hostname=self.hostname,
            opts=InvokeOutputOptions(depends_on=[self.container]),
        )
        self.ipv4 = self.device.apply(lambda x: IPv4Address(x.addresses[0]))
        self.ipv6 = self.device.apply(lambda x: IPv6Address(x.addresses[1]))

        self.private_ips: dict[str, Output[IPvAnyAddress]] = {
            "v4": self.ipv4,
            "v6": self.ipv6,
        }
        outputs = self.container_outputs() | {
            "ip{}".format(k): v.apply(str) for k, v in self.private_ips.items()
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
