from ipaddress import IPv4Address, IPv6Address

import pulumi
import pulumi_tailscale as tailscale
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import InvokeOutputOptions, Output, ResourceOptions
from pydantic import IPvAnyAddress


class TailscaleService(ServiceResourceBase):
    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions | None,
        hostname: str,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.hostname = hostname
        self.options[None] = ContainerModelBuildArgs(
            opts=ResourceOptions(delete_before_replace=True),
            envs={
                "TS_AUTHKEY": self.build_authkey().key,
                "TS_HOSTNAME": self.hostname,
            },
        )
        self.build_containers()

        self.device = tailscale.get_device_output(
            hostname=self.hostname,
            opts=InvokeOutputOptions(depends_on=[self.container]),
        )
        self.ipv4 = self.device.apply(lambda x: IPv4Address(x.addresses[0]))
        self.ipv6 = self.device.apply(lambda x: IPv6Address(x.addresses[1]))

        self.ips: dict[str, Output[IPvAnyAddress]] = {
            "v4": self.ipv4,
            "v6": self.ipv6,
        }

        pulumi.export("tailscale.ipv4", self.ipv4.apply(str))
        pulumi.export("tailscale.ipv6", self.ipv6.apply(str))
        self.register_outputs({})

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
