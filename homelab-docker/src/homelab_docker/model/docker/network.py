from typing import Self

import pulumi_docker as docker
from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPAddress, IPNetwork
from pulumi import ResourceOptions
from pydantic import ValidationError, model_validator


class BridgeIpamNetworkModel(HomelabBaseModel):
    subnet: IPNetwork
    gateway: IPAddress | None = None
    ip_range: IPNetwork | None = None

    @model_validator(mode="after")
    def set_gateway_and_check_ip_range(self) -> Self:
        gateway = self.gateway or (self.subnet.network + 1)

        if self.ip_range:
            if self.ip_range not in self.subnet:
                raise ValidationError("Subnet must contain the ip range")
            ip_range = self.ip_range
        else:
            ip_range = self.subnet

        return self.model_construct(
            subnet=self.subnet, gateway=gateway, ip_range=ip_range
        )

    def to_args(self) -> docker.NetworkIpamConfigArgs:
        return docker.NetworkIpamConfigArgs(
            subnet=str(self.subnet),
            gateway=str(self.gateway) if self.gateway else None,
            ip_range=str(self.ip_range) if self.ip_range else None,
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
    ) -> docker.Network:
        options = self.options
        if not self.icc:
            options["enable_icc"] = "false"

        return docker.Network(
            resource_name,
            opts=opts,
            driver="bridge",
            ipv6=self.ipv6,
            internal=self.internal,
            ipam_configs=[ipam.to_args() for ipam in self.ipam] if self.ipam else None,
            labels=[
                docker.NetworkLabelArgs(label=k, value=v)
                for k, v in (project_labels | self.labels).items()
            ],
            options={
                "com.docker.network.bridge.{}".format(k): v
                for k, v in self.options.items()
            },
        )
