from homelab_docker.container.volume import Volume

from homelab.docker.service.tailscale import Tailscale


def build_config(config_volume: Volume, tailscale: Tailscale) -> dict:
    return {
        "global": {"checkNewVersion": False, "sendAnonymousUsage": False},
        "entryPoints": {
            "https-private": {
                "address": "[::]:443",
                "forwardedHeaders": {"insecure": True},
            },
            "https-public": {
                "address": "[::]:{}".format(
                    tailscale.config().container.ports["httpsv4"].internal
                ),
            },
            "http-private": {
                "address": "[::]:80",
                "http": {
                    "redirections": {"entryPoint": {"to": ":443", "scheme": "https"}}
                },
            },
            "http-public": {
                "address": "[::]:{}".format(
                    tailscale.config().container.ports["httpv4"].internal
                ),
                "http": {
                    "redirections": {"entryPoint": {"to": ":443", "scheme": "https"}}
                },
            },
            "providers": {
                "file": {"directory": config_volume.to_path(), "watch": True},
            },
            "api": {
                "basePath": "/proxy",
                "dashboard": True,
                "disableDashboardAd": True,
            },
            "ping": {},
            "log": {"level": "INFO", "format": "json"},
            "accessLog": {"format": "json", "fields": {"names": {"StartUTC": "drop"}}},
        },
    }
