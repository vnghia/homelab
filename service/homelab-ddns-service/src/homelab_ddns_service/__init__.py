from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
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
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.settings = [
            {
                "provider": "cloudflare",
                "zone_identifier": record.zone_id,
                "domain": hostname.value,
                "ttl": 1,
                "token": network_resource.token.ddns_tokens[
                    self.extractor_args.host.name
                ].value,
                "ip_version": ip_version,
            }
            for record in network_resource.config.records.values()
            if record.is_ddns and record.host == self.extractor_args.host.name
            for hostname in record.hostnames.values()
            for ip_version in ["ipv4", "ipv6"]
        ]
        self.options[None].add_envs(
            {"CONFIG": Output.json_dumps({"settings": self.settings})}
        )
        self.build(None)
