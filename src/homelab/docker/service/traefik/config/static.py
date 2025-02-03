from homelab_config.docker.service import Service as Config
from homelab_docker.file import File
from homelab_docker.file.config import ConfigFile
from homelab_docker.volume_path import VolumePath
from pulumi import ResourceOptions

from homelab.docker.resource import Resource
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.service.traefik.config.service import Service


class Static:
    PUBLIC_CERT_RESOLVER = "public-cert-resolver"
    PRIVATE_CERT_RESOLVER = "private-cert-resolver"

    def __init__(self, config: Config, tailscale: Tailscale) -> None:
        self.service_config = config.config(Service)
        self.container_volumes = config.container.volumes

        self.volume_path = VolumePath.model_validate(
            config.container.command[-1].data if config.container.command else None
        )
        self.volume_config = self.container_volumes[self.volume_path.volume]
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
                        tailscale.config().container.ports["httpv4"].internal
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
                        tailscale.config().container.ports["httpsv4"].internal
                    ),
                },
            },
            "providers": {
                "file": {
                    "directory": (
                        self.volume_config.to_path() / self.provider_directory
                    ).as_posix(),
                    "watch": True,
                },
            },
            "certificatesResolvers": {
                self.PUBLIC_CERT_RESOLVER: {
                    "acme": {
                        "caServer": str(self.service_config.acme.server),
                        "email": self.service_config.acme.email,
                        "storage": self.service_config.acme.storage.to_str(
                            self.container_volumes
                        ),
                        "httpChallenge": {
                            "entryPoint": self.service_config.entrypoint.public_http
                        },
                    }
                },
                self.PRIVATE_CERT_RESOLVER: {
                    "acme": {
                        "caServer": str(self.service_config.acme.server),
                        "email": self.service_config.acme.email,
                        "storage": self.service_config.acme.storage.to_str(
                            self.container_volumes
                        ),
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

    def get_dynamic_volume_path(self, file: str) -> VolumePath:
        return self.volume_path.model_copy(
            update={"path": (self.provider_directory / file).with_suffix(".toml")}
        )

    def build_resource(
        self, resource: Resource, opts: ResourceOptions | None = None
    ) -> File:
        return ConfigFile(
            volume_path=self.volume_path,
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
        ).build_resource("static", resource=resource.to_docker_resource(), opts=opts)
