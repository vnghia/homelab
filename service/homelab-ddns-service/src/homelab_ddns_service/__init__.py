from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_extra_service import ExtraService
from homelab_network.resource.network import NetworkResource
from pulumi import Output, ResourceOptions

from .config import DdnsConfig


class DdnsService(ExtraService[DdnsConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[DdnsConfig],
        *,
        opts: ResourceOptions,
        network_resource: NetworkResource,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
        self.settings = [
            {
                "provider": "cloudflare",
                "zone_identifier": record.zone_id,
                "domain": hostname.value,
                "ttl": 1,
                "token": network_resource.token.ddns_tokens[
                    self.docker_resource_args.host
                ].value,
                "ip_version": ip_version,
            }
            for record in network_resource.config.records.values()
            if record.is_ddns and record.host == docker_resource_args.host
            for hostname in record.hostnames.values()
            for ip_version in ["ipv4", "ipv6"]
        ]
        self.options[None].envs = {
            "CONFIG": Output.json_dumps({"settings": self.settings})
        }
        self.build()
