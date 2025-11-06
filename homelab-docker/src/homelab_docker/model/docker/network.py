from typing import Any

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from pulumi import Output, ResourceOptions
from pydantic import IPvAnyAddress, IPvAnyNetwork


class BridgeIpamNetworkModel(HomelabBaseModel):
    subnet: IPvAnyNetwork

    _gateway: IPvAnyAddress
    _ip_range: IPvAnyNetwork

    def model_post_init(self, context: Any, /) -> None:
        self._gateway = self.subnet.network_address + 1
        self._ip_range = self.subnet

    @property
    def gateway(self) -> IPvAnyAddress:
        return self._gateway

    @property
    def ip_range(self) -> IPvAnyNetwork:
        return self._ip_range

    def to_args(self) -> docker.NetworkIpamConfigArgs:
        return docker.NetworkIpamConfigArgs(
            subnet=str(self.subnet),
            gateway=str(self.gateway),
            ip_range=str(self.ip_range),
        )


class BridgeNetworkModel(HomelabBaseModel):
    ipv6: bool = True
    internal: bool = False
    ipam: list[BridgeIpamNetworkModel] = []
    icc: bool = True
    labels: dict[str, str] = {}
    options: dict[str, str] = {}

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        project_labels: dict[str, str],
        ipam: list[Output[BridgeIpamNetworkModel]],
    ) -> docker.Network:
        options = self.options
        if not self.icc:
            options["enable_icc"] = "false"

        has_static_ipam = bool(self.ipam) or bool(ipam)

        return docker.Network(
            resource_name,
            opts=ResourceOptions.merge(
                opts,
                ResourceOptions(
                    delete_before_replace=opts.delete_before_replace or has_static_ipam
                ),
            ),
            driver="bridge",
            ipv6=self.ipv6,
            internal=self.internal,
            ipam_configs=[ipam.to_args() for ipam in self.ipam]
            + [ipam.apply(BridgeIpamNetworkModel.to_args) for ipam in ipam]
            if has_static_ipam
            else None,
            labels=[
                docker.NetworkLabelArgs(label=k, value=v)
                for k, v in (project_labels | self.labels).items()
            ],
            options={
                "com.docker.network.bridge.{}".format(k): v
                for k, v in self.options.items()
            },
        )
