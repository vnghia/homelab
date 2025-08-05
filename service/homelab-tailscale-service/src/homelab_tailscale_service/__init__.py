from ipaddress import IPv4Address, IPv6Address

import pulumi
import pulumi_tailscale as tailscale
from homelab_docker.config.network import NetworkConfig
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from homelab_network.model.ip import NetworkIpOutputModel
from pulumi import InvokeOutputOptions, ResourceOptions


class TailscaleService(ServiceResourceBase):
    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions,
        hostname: str,
        internal_aliases: list[str],
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
            aliases={
                NetworkConfig.INTERNAL_BRIDGE: internal_aliases,
                NetworkConfig.PROXY_BRIDGE: [NetworkConfig.PROXY_ALIAS],
            },
        )
        self.build_containers()

        self.device = tailscale.get_device_output(
            hostname=self.hostname,
            opts=InvokeOutputOptions(depends_on=[self.container.resource]),
        )
        self.ipv4 = self.device.apply(lambda x: IPv4Address(x.addresses[0]))
        self.ipv6 = self.device.apply(lambda x: IPv6Address(x.addresses[1]))
        self.ip = NetworkIpOutputModel(v4=self.ipv4, v6=self.ipv6)

        pulumi.export(
            "{}.tailscale.ipv4".format(self.docker_resource_args.host),
            self.ipv4.apply(str),
        )
        pulumi.export(
            "{}.tailscale.ipv6".format(self.docker_resource_args.host),
            self.ipv6.apply(str),
        )
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
