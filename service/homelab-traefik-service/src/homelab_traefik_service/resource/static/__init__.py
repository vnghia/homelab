from __future__ import annotations

import typing

from homelab_docker.extract.service import ServiceExtractor
from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from homelab_network.config.port import NetworkPortConfig
from pulumi import ResourceOptions

from . import schema

if typing.TYPE_CHECKING:
    from ... import TraefikService


class TraefikStaticConfigResource(
    ConfigFileResource[schema.TraefikV3StaticConfiguration],
    module="traefik",
    name="StaticConfig",
):
    validator = schema.TraefikV3StaticConfiguration
    dumper = TomlDumper[schema.TraefikV3StaticConfiguration]

    CERT_RESOLVER = "cert-resolver"

    def __init__(
        self,
        *,
        opts: ResourceOptions,
        traefik_service: TraefikService,
        port: NetworkPortConfig,
    ) -> None:
        traefik_config = traefik_service.config
        traefik_model = traefik_service.model[None]

        static_volume_path = ServiceExtractor(
            traefik_service.config.path.static
        ).extract_volume_path(traefik_service, None)

        timeouts = {
            "respondingTimeouts": {
                "readTimeout": traefik_config.timeout.read,
                "writeTimeout": traefik_config.timeout.idle,
                "idleTimeout": traefik_config.timeout.write,
            }
        }

        proxy_protocol = (
            {
                "proxyProtocol": {
                    "trustedIPs": traefik_service.docker_resource_args.network.proxy_bridge.ipam_configs.apply(
                        lambda ipam_configs: [
                            str(ip) for ip in traefik_config.proxy_protocol.ips
                        ]
                        + [
                            ipam_config.subnet
                            for ipam_config in ipam_configs
                            if ipam_config.subnet
                        ]
                    )
                }
            }
            if traefik_config.proxy_protocol.enabled
            else {}
        )

        super().__init__(
            "static",
            opts=opts,
            volume_path=static_volume_path,
            data={
                "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
                "accessLog": {"format": "json"},
                "api": {
                    "basePath": ServiceExtractor(traefik_config.path.api).extract_str(
                        traefik_service, None
                    ),
                    "dashboard": True,
                    "disableDashboardAd": True,
                },
                "log": {"level": "INFO", "format": "json"},
                "ping": {},
                "entryPoints": {
                    traefik_config.entrypoint.private_http: {
                        "address": "[::]:{}".format(port.HTTP),
                        "http": {
                            "redirections": {
                                "entryPoint": {
                                    "to": ":{}".format(port.HTTPS),
                                    "scheme": "https",
                                }
                            }
                        },
                    },
                    traefik_config.entrypoint.public_http: {
                        "address": "[::]:{}".format(port.internal.http),
                        "http": {
                            "redirections": {
                                "entryPoint": {
                                    "to": ":{}".format(port.external.https),
                                    "scheme": "https",
                                }
                            }
                        },
                    }
                    | proxy_protocol,
                    traefik_config.entrypoint.private_https: {
                        "address": "[::]:{}".format(port.HTTPS),
                        "http3": {},
                        "transport": timeouts,
                    },
                    traefik_config.entrypoint.public_https: {
                        "address": "[::]:{}".format(port.internal.https),
                        "http3": {"advertisedPort": port.external.https},
                        "transport": timeouts,
                    }
                    | proxy_protocol,
                },
                "providers": {
                    "file": {
                        "directory": traefik_service.dynamic_directory_volume_path.to_path(
                            traefik_service, traefik_model
                        ),
                        "watch": True,
                    },
                },
                "serversTransport": {"insecureSkipVerify": True},
                "certificatesResolvers": {
                    self.CERT_RESOLVER: {
                        "acme": {
                            "caServer": str(traefik_config.acme.server),
                            "email": traefik_config.acme.email,
                            "storage": ServiceExtractor(
                                traefik_config.acme.storage
                            ).extract_path(traefik_service, None),
                            "dnsChallenge": {
                                "provider": "cloudflare",
                                "resolvers": ["1.1.1.1:53", "8.8.8.8:53"],
                                "propagation": {
                                    "disableChecks": traefik_config.acme.disable_checks,
                                    "requireAllRNS": traefik_config.acme.require_all_rns,
                                    "disableANSChecks": traefik_config.acme.disable_ans_checks,
                                    "delayBeforeChecks": traefik_config.acme.delay_before_checks,
                                },
                            },
                        }
                    },
                },
                "experimental": {
                    "plugins": {
                        name: {
                            "moduleName": model.name,
                            "version": model.version,
                        }
                        for name, model in traefik_config.plugins.items()
                    },
                },
            },
            volume_resource=traefik_service.docker_resource_args.volume,
        )
