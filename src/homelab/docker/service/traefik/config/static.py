from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.file.config import ConfigFile
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.volume import VolumeResource
from homelab_network.config.network import NetworkConfig
from pulumi import ResourceOptions

from homelab.docker.service.tailscale import TailscaleService
from homelab.docker.service.traefik.config import TraefikConfig


class TraefikStaticConfig:
    PUBLIC_CERT_RESOLVER = "public-cert-resolver"
    PRIVATE_CERT_RESOLVER = "private-cert-resolver"

    def __init__(
        self,
        network_config: NetworkConfig,
        traefik_service_model: ServiceModel[TraefikConfig],
        tailscale_service: TailscaleService,
    ) -> None:
        self.network_config = network_config
        container_volumes_config = traefik_service_model.container.volumes
        self.service_config = traefik_service_model.config

        self.container_volume_path = ContainerVolumePath.model_validate(
            traefik_service_model.container.command[-1].root
            if traefik_service_model.container.command
            else None
        )
        self.container_volume_config = container_volumes_config[
            self.container_volume_path.volume
        ]
        self.provider_directory = self.service_config.provider.file

        self.data = {
            "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
            "accessLog": {"format": "json"},
            "api": {
                "basePath": self.service_config.path,
                "dashboard": True,
                "disableDashboardAd": True,
            },
            "log": {"level": "INFO", "format": "json"},
            "ping": {},
            "entryPoints": {
                self.service_config.entrypoint.private_http: {
                    "address": "[::]:80",
                    "http": {
                        "redirections": {
                            "entryPoint": {"to": ":443", "scheme": "https"}
                        }
                    },
                },
                self.service_config.entrypoint.public_http: {
                    "address": "[::]:{}".format(
                        tailscale_service.model.container.ports["httpv4"].internal
                    ),
                    "http": {
                        "redirections": {
                            "entryPoint": {"to": ":443", "scheme": "https"}
                        }
                    },
                },
                self.service_config.entrypoint.private_https: {
                    "address": "[::]:443",
                    "forwardedHeaders": {"insecure": True},
                },
                self.service_config.entrypoint.public_https: {
                    "address": "[::]:{}".format(
                        tailscale_service.model.container.ports["httpsv4"].internal
                    ),
                },
            },
            "providers": {
                "file": {
                    "directory": (
                        self.container_volume_config.to_container_path()
                        / self.provider_directory
                    ).as_posix(),
                    "watch": True,
                },
            },
            "certificatesResolvers": {
                self.PUBLIC_CERT_RESOLVER: {
                    "acme": {
                        "caServer": str(self.service_config.acme.server),
                        "email": self.service_config.acme.email,
                        "storage": self.service_config.acme.storage.public.to_container_path(
                            container_volumes_config
                        ).as_posix(),
                        "httpChallenge": {
                            "entryPoint": self.service_config.entrypoint.public_http
                        },
                    }
                },
                self.PRIVATE_CERT_RESOLVER: {
                    "acme": {
                        "caServer": str(self.service_config.acme.server),
                        "email": self.service_config.acme.email,
                        "storage": self.service_config.acme.storage.private.to_container_path(
                            container_volumes_config
                        ).as_posix(),
                        "dnsChallenge": {
                            "provider": "cloudflare",
                            "propagation": {
                                "delayBeforeChecks": 300,
                            },
                        },
                    }
                },
            },
        }

    def get_dynamic_container_volume_path(self, file: str) -> ContainerVolumePath:
        return self.container_volume_path.model_copy(
            update={"path": (self.provider_directory / file).with_suffix(".toml")}
        )

    def build_resource(
        self, *, opts: ResourceOptions | None, volume_resource: VolumeResource
    ) -> FileResource:
        return ConfigFile(
            container_volume_path=self.container_volume_path,
            data=self.data,
            schema_url="https://json.schemastore.org/traefik-v3.json",
            schema_override={
                "$defs": {
                    "acmeDNSChallengePropagation": {
                        "additionalProperties": False,
                        "properties": {
                            "delayBeforeChecks": {"type": "number"},
                        },
                        "type": "object",
                    },
                    "acmeDNSChallenge": {
                        "properties": {
                            "propagation": {
                                "$ref": "#/$defs/acmeDNSChallengePropagation"
                            }
                        }
                    },
                    "staticAPI": {"properties": {"basePath": {"type": "string"}}},
                }
            },
        ).build_resource("static", opts=opts, volume_resource=volume_resource)
