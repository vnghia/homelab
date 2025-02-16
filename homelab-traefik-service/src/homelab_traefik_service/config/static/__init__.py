from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from homelab_tailscale_service import TailscaleService
from pulumi import ResourceOptions

from .. import TraefikConfig
from . import schema


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
        traefik_service_model: ServiceModel[TraefikConfig],
        tailscale_service: TailscaleService,
    ) -> None:
        container_volumes_config = traefik_service_model.container.volumes
        traefik_config = traefik_service_model.config

        container_volume_path = ContainerVolumePath.model_validate(
            traefik_service_model.container.command[-1].root
            if traefik_service_model.container.command
            else None
        )
        self.dynamic_directory_container_volume_path = container_volume_path.model_copy(
            update={"path": traefik_config.provider.file}
        )

        super().__init__(
            ConfigFileModel(
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
                                tailscale_service.model.container.ports[
                                    "httpv4"
                                ].internal
                            ),
                            "http": {
                                "redirections": {
                                    "entryPoint": {"to": ":443", "scheme": "https"}
                                }
                            },
                        },
                        traefik_config.entrypoint.private_https: {
                            "address": "[::]:443"
                        },
                        traefik_config.entrypoint.public_https: {
                            "address": "[::]:{}".format(
                                tailscale_service.model.container.ports[
                                    "httpsv4"
                                ].internal
                            ),
                        },
                    },
                    "providers": {
                        "file": {
                            "directory": self.dynamic_directory_container_volume_path.to_container_path(
                                container_volumes_config
                            ).as_posix(),
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
                                ).as_posix(),
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
                                ).as_posix(),
                                "dnsChallenge": {"provider": "cloudflare"},
                            }
                        },
                    },
                },
            ),
            "static",
            opts=opts,
            volume_resource=tailscale_service.docker_resource_args.volume,
        )
