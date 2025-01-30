from homelab_docker.file import File
from homelab_docker.file.config import ConfigFile
from homelab_docker.volume_path import VolumePath
from pulumi import ResourceOptions

from homelab.config.docker.service import Service as Config
from homelab.docker.resource import Resource
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.service.traefik.config.service import Service


class Static:
    def __init__(self, config: Config, tailscale: Tailscale) -> None:
        self.service_config = config.config(Service)
        self.volume_path = VolumePath.model_validate(
            config.container.command[-1].data if config.container.command else None
        )
        self.volume_config = config.container.volumes[self.volume_path.volume]

        self.data = {
            "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
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
                        self.volume_config.to_path() / self.service_config.provider.file
                    ).as_posix(),
                    "watch": True,
                },
            },
            "api": {
                "basePath": self.service_config.api,
                "dashboard": True,
                "disableDashboardAd": True,
            },
            "ping": {},
            "log": {"level": "INFO", "format": "json"},
            "accessLog": {"format": "json", "fields": {"names": {"StartUTC": "drop"}}},
        }

    def build_resource(
        self, resource: Resource, opts: ResourceOptions | None = None
    ) -> File:
        return ConfigFile(volume_path=self.volume_path, data=self.data).build_resource(
            "static", resource=resource.to_docker_resource(), opts=opts
        )
