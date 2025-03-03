from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from homelab_tailscale_service import TailscaleService
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
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        tailscale_service: TailscaleService,
    ) -> None:
        traefik_config = traefik_service.config
        traefik_model = traefik_service.model[None]
        tailscale_model = tailscale_service.model[None]

        static_volume_path = traefik_service.config.path.static.extract_volume_path(
            traefik_service, None
        )

        proxy_protocol = (
            {
                "proxyProtocol": {
                    "trustedIPs": [str(ip) for ip in traefik_config.proxy_protocol.ips]
                }
            }
            if traefik_config.proxy_protocol.ips
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
                    "basePath": traefik_config.path.api.extract_str(
                        traefik_service, None
                    ),
                    "dashboard": True,
                    "disableDashboardAd": True,
                },
                "log": {"level": "INFO", "format": "json"},
                "ping": {},
                "entryPoints": {
                    traefik_config.entrypoint.private_http: {
                        "address": "[::]:80",
                        "http": {
                            "redirections": {
                                "entryPoint": {"to": ":443", "scheme": "https"}
                            }
                        },
                    },
                    traefik_config.entrypoint.public_http: {
                        "address": "[::]:{}".format(
                            tailscale_model.ports["httpv4"].internal
                        ),
                        "http": {
                            "redirections": {
                                "entryPoint": {"to": ":443", "scheme": "https"}
                            }
                        },
                    }
                    | proxy_protocol,
                    traefik_config.entrypoint.private_https: {
                        "address": "[::]:443",
                        "http3": {},
                    },
                    traefik_config.entrypoint.public_https: {
                        "address": "[::]:{}".format(
                            tailscale_model.ports["httpsv4"].internal
                        ),
                        "http3": {},
                    }
                    | proxy_protocol,
                },
                "providers": {
                    "file": {
                        "directory": traefik_service.dynamic_directory_volume_path.to_path(
                            traefik_model
                        ),
                        "watch": True,
                    },
                },
                "certificatesResolvers": {
                    self.CERT_RESOLVER: {
                        "acme": {
                            "caServer": str(traefik_config.acme.server),
                            "email": traefik_config.acme.email,
                            "storage": traefik_config.acme.storage.extract_path(
                                traefik_service, None
                            ),
                            "dnsChallenge": {
                                "provider": "cloudflare",
                                "resolvers": ["1.1.1.1:53", "8.8.8.8:53"],
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
