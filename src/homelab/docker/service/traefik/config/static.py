from homelab.config.docker import Service as Config
from homelab.docker.service.tailscale import Tailscale
from homelab.docker.service.traefik.config.service import Service


class Static:
    def __init__(self, config: Config, tailscale: Tailscale) -> None:
        service_config = config.config(Service)
        self.data = {
            "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
            "entryPoints": {
                service_config.entrypoint.private_http: {
                    "address": "[::]:80",
                    "http": {
                        "redirections": {
                            "entryPoint": {"to": ":443", "scheme": "https"}
                        }
                    },
                },
                service_config.entrypoint.public_http: {
                    "address": "[::]:{}".format(
                        tailscale.config().container.ports["httpv4"].internal
                    ),
                    "http": {
                        "redirections": {
                            "entryPoint": {"to": ":443", "scheme": "https"}
                        }
                    },
                },
                service_config.entrypoint.private_https: {
                    "address": "[::]:443",
                    "forwardedHeaders": {"insecure": True},
                },
                service_config.entrypoint.public_https: {
                    "address": "[::]:{}".format(
                        tailscale.config().container.ports["httpsv4"].internal
                    ),
                },
            },
            "providers": {
                "file": {
                    "directory": (
                        config.container.volumes[service_config.volume].to_path()
                        / service_config.provider.file
                    ).as_posix(),
                    "watch": True,
                },
            },
            "api": {
                "basePath": service_config.api,
                "dashboard": True,
                "disableDashboardAd": True,
            },
            "ping": {},
            "log": {"level": "INFO", "format": "json"},
            "accessLog": {"format": "json", "fields": {"names": {"StartUTC": "drop"}}},
        }
