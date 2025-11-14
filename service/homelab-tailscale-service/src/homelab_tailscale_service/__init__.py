import pulumi
import pulumi_tailscale as tailscale
from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_network.model.ip import NetworkIpModel, NetworkIpOutputModel
from pulumi import ResourceOptions

from .resource.device import TailscaleDeviceResource


class TailscaleService(ServiceResourceBase):
    def __init__(
        self,
        model: ServiceModel,
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.options[None].add_envs({"TS_AUTHKEY": self.build_authkey().key})
        self.build_containers()

        self.device = TailscaleDeviceResource(
            opts=self.child_opts, tailscale_service=self
        )
        self.ip = NetworkIpOutputModel(
            {NetworkIpModel.V4: self.device.v4, NetworkIpModel.V6: self.device.v6}
        )

        pulumi.export(
            "{}.tailscale.ipv4".format(self.extractor_args.host.name),
            self.device.v4.apply(str),
        )
        pulumi.export(
            "{}.tailscale.ipv6".format(self.extractor_args.host.name),
            self.device.v6.apply(str),
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
