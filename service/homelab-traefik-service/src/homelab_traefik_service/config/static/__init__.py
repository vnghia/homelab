from __future__ import annotations

import typing

from homelab_docker.model.container.volume_path import ContainerVolumePath
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

    PUBLIC_CERT_RESOLVER = "public-cert-resolver"
    PRIVATE_CERT_RESOLVER = "private-cert-resolver"

    def __init__(
        self,
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        tailscale_service: TailscaleService,
    ) -> None:
        traefik_config = traefik_service.model.config
        traefik_service_model = traefik_service.model.container
        container_volumes_config = traefik_service_model.volumes

        container_volume_path = ContainerVolumePath.model_validate(
            traefik_service_model.command[-1].root
            if traefik_service_model.command
            else None
        )
        self.dynamic_directory_container_volume_path = (
            container_volume_path.__replace__(path=traefik_config.provider.file)
        )

        super().__init__(
            "static",
            opts=opts,
            container_volume_path=container_volume_path,
            data={
                "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
                "accessLog": {"format": "json"},
                "api": {
                    "basePath": traefik_config.path,
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
                            tailscale_service.model.container.ports["httpv4"].internal
                        ),
                        "http": {
                            "redirections": {
                                "entryPoint": {"to": ":443", "scheme": "https"}
                            }
                        },
                    },
                    traefik_config.entrypoint.private_https: {"address": "[::]:443"},
                    traefik_config.entrypoint.public_https: {
                        "address": "[::]:{}".format(
                            tailscale_service.model.container.ports["httpsv4"].internal
                        ),
                    },
                },
                "providers": {
                    "file": {
                        "directory": self.dynamic_directory_container_volume_path.to_container_path(
                            container_volumes_config
                        ),
                        "watch": True,
                    },
                },
                "certificatesResolvers": {
                    self.PUBLIC_CERT_RESOLVER: {
                        "acme": {
                            "caServer": str(traefik_config.acme.server),
                            "email": traefik_config.acme.email,
                            "storage": traefik_config.acme.storage.public.to_container_path(
                                container_volumes_config
                            ),
                            "httpChallenge": {
                                "entryPoint": traefik_config.entrypoint.public_http
                            },
                        }
                    },
                    self.PRIVATE_CERT_RESOLVER: {
                        "acme": {
                            "caServer": str(traefik_config.acme.server),
                            "email": traefik_config.acme.email,
                            "storage": traefik_config.acme.storage.private.to_container_path(
                                container_volumes_config
                            ),
                            "dnsChallenge": {"provider": "cloudflare"},
                        }
                    },
                },
            },
            volume_resource=traefik_service.docker_resource_args.volume,
        )
