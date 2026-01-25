from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import Output


def pre_build(service: ExtraService[ExtraConfig]) -> None:
    network_resource = service.extractor_args.host.network
    host_name = service.extractor_args.host.name

    settings = [
        {
            "provider": "cloudflare",
            "zone_identifier": record.zone_id,
            "domain": hostname.value,
            "ttl": 1,
            "token": network_resource.token.ddns_tokens[host_name].value,
            "ip_version": ip_version,
        }
        for record in network_resource.config.records.values()
        if record.is_ddns and record.host == host_name
        for hostname in record.hostnames.values()
        for ip_version in ["ipv4", "ipv6"]
    ]

    service.options[None].add_envs(
        {"CONFIG": Output.json_dumps({"settings": settings})}
    )


def post_build(service: ExtraService[ExtraConfig]) -> None:
    pass
