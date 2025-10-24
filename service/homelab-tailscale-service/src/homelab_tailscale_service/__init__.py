import pulumi
import pulumi_tailscale as tailscale
from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.docker.container import ContainerModelBuildArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_network.model.ip import NetworkIpOutputModel
from netaddr_pydantic import IPv4Address, IPv6Address
from pulumi import InvokeOutputOptions, ResourceOptions
from pydantic import TypeAdapter


class TailscaleService(ServiceResourceBase):
    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.options[None] = ContainerModelBuildArgs(
            opts=ResourceOptions(delete_before_replace=True),
            envs={"TS_AUTHKEY": self.build_authkey().key},
        )
        self.build_containers()

        self.device = tailscale.get_device_output(
            hostname=self.container.resource.hostname,
            opts=InvokeOutputOptions(depends_on=[self.container.resource]),
        )
        self.ipv4 = self.device.apply(
            lambda x: TypeAdapter(IPv4Address).validate_python(x.addresses[0])
        )
        self.ipv6 = self.device.apply(
            lambda x: TypeAdapter(IPv6Address).validate_python(x.addresses[1])
        )
        self.ip = NetworkIpOutputModel(v4=self.ipv4, v6=self.ipv6)

        pulumi.export(
            "{}.tailscale.ipv4".format(self.extractor_args.host.name()),
            self.ipv4.apply(str),
        )
        pulumi.export(
            "{}.tailscale.ipv6".format(self.extractor_args.host.name()),
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
