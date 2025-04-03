from homelab_docker.extract.service import ServiceExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import GluetunConfig


class GluetunService(ServiceWithConfigResourceBase[GluetunConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[GluetunConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        if self.config.opvn:
            self.opvn = FileResource(
                "opvn",
                opts=self.child_opts,
                volume_path=ServiceExtractor(self.config.opvn_path).extract_volume_path(
                    self, self.model.containers[None]
                ),
                content=self.config.opvn,
                mode=0o444,
                volume_resource=self.docker_resource_args.volume,
            )
            self.options[None].files = [self.opvn]

        self.options[None].envs = {
            "FIREWALL_VPN_INPUT_PORTS": ",".join(
                map(
                    str,
                    sorted(self.docker_resource_args.config.vpn.ports.values()),
                )
            )
        }
        self.build_containers()

        self.register_outputs({})
