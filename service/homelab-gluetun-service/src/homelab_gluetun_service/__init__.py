from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import GluetunConfig


class GluetunService(ServiceWithConfigResourceBase[GluetunConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[GluetunConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        if self.config.open_vpn:
            self.open_vpn = FileResource(
                "opvn",
                opts=self.child_opts,
                volume_path=GlobalExtractor(
                    self.config.open_vpn.path
                ).extract_volume_path(self.extractor_args),
                content=GlobalExtractor(self.config.open_vpn.content).extract_str(
                    self.extractor_args
                ),
                mode=0o444,
                extractor_args=extractor_args,
            )
            self.options[None].files = [self.open_vpn]
            self.options[None].envs = {
                "OPENVPN_CUSTOM_CONFIG": self.open_vpn.to_path(
                    self.extractor_args
                ).as_posix()
            }

        self.options[None].envs = {
            "FIREWALL_VPN_INPUT_PORTS": ",".join(
                map(
                    str,
                    sorted(self.extractor_args.host_model.vpn_.ports.values()),
                )
            )
        }
        self.build_containers()

        self.register_outputs({})
