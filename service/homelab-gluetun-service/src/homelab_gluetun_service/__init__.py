from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.service import ServiceExtractor
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

        if self.config.opvn:
            self.opvn = FileResource(
                "opvn",
                opts=self.child_opts,
                volume_path=ServiceExtractor(self.config.opvn_path).extract_volume_path(
                    self.extractor_args
                ),
                content=self.config.opvn,
                mode=0o444,
                extractor_args=extractor_args,
            )
            self.options[None].files = [self.opvn]

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
