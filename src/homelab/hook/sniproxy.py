from typing import Any

from homelab_docker.config.docker.network import NetworkEgressType
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.file.config import YamlDumper
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from pulumi import Output


def pre_build(service: ExtraService[ExtraConfig]) -> None:
    http_bind = service.extract_variable_str("HTTP_BIND")
    https_bind = service.extract_variable_str("HTTPS_BIND")

    https_egress_port = service.extract_variable_str("HTTPS_EGRESS_PORT")

    routes: list[Any] = []
    service_egresses = service.extractor_args.host.docker.network.service_egresses
    for service_egress in service_egresses.values():
        for egress_type, egresses in service_egress.items():
            match egress_type:
                case NetworkEgressType.HTTPS:
                    routes.extend(
                        {
                            "domains": domains,
                            "backend": {
                                "address": Output.format(
                                    "{}:{}", address, https_egress_port
                                )
                            },
                        }
                        for egress in egresses.values()
                        if egress.proxied
                        and (
                            domains := [
                                GlobalExtractor(address).extract_str(
                                    service.extractor_args
                                )
                                for address in egress.addresses
                            ]
                        )
                        and (
                            address := GlobalExtractor(egress.ip).extract_str(
                                service.extractor_args
                            )
                            if egress.ip
                            else domains[0]
                        )
                    )

    service.options[None].add_files(
        [
            FileResource(
                "config",
                opts=service.child_opts,
                volume_path=service.extract_variable_volume_path("CONFIG_PATH"),
                content=YamlDumper.dumps_output(
                    {"bind_http": http_bind, "bind_https": https_bind, "routes": routes}
                ),
                permission=service.user,
                extractor_args=service.extractor_args,
            )
        ]
    )


def post_build(service: ExtraService[ExtraConfig]) -> None:
    pass
