from typing import Any

import pulumi_docker as docker
from homelab_docker.model.file.config import ConfigFile
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.volume import VolumeResource
from homelab_network.config.network import NetworkConfig
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, PositiveInt

from ..static import TraefikStaticConfig
from .middleware import TraefikMiddleware
from .service import TraefikService, TraefikServiceType


class TraefikHttpDynamicConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    public: bool
    hostname: str | None = None
    prefix: str | None = None

    rules: list[str] = []
    service: TraefikService | PositiveInt | str
    middlewares: list[TraefikMiddleware | str] = []

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        network_config: NetworkConfig,
        volume_resource: VolumeResource,
        containers: dict[str, docker.Container],
        static_config: TraefikStaticConfig,
    ) -> FileResource:
        entrypoint = static_config.service_config.entrypoint
        host = (
            network_config.public.hostnames
            if self.public
            else network_config.private.hostnames
        )[self.hostname or self.name]

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    self.name: {
                        "service": self.name
                        if isinstance(self.service, (TraefikService, int))
                        else self.service,
                        "entryPoints": [
                            entrypoint.public_https
                            if self.public
                            else entrypoint.private_https
                        ],
                        "rule": " && ".join(
                            ["Host(`{}`)".format(host)]
                            + (
                                ["PathPrefix(`{}`)".format(self.prefix)]
                                if self.prefix
                                else []
                            )
                            + self.rules
                        ),
                        "middlewares": [
                            middleware.name
                            if isinstance(middleware, TraefikMiddleware)
                            else middleware
                            for middleware in self.middlewares
                        ],
                        "tls": {
                            "certResolver": static_config.PUBLIC_CERT_RESOLVER
                            if self.public
                            else static_config.PRIVATE_CERT_RESOLVER
                        },
                    }
                },
            }
        }

        if isinstance(self.service, TraefikService):
            data["http"]["services"] = {
                self.name: {
                    "loadBalancer": {
                        "servers": [
                            {
                                "url": self.service.to_url(
                                    TraefikServiceType.HTTP, self.name, containers
                                ).apply(str)
                            }
                        ]
                    }
                }
            }
        elif isinstance(self.service, int):
            data["http"]["services"] = {
                self.name: {
                    "loadBalancer": {
                        "servers": [
                            {
                                "url": TraefikService(port=self.service)
                                .to_url(TraefikServiceType.HTTP, self.name, containers)
                                .apply(str)
                            }
                        ]
                    }
                }
            }

        middlewares = {
            middleware.name: middleware.data
            for middleware in self.middlewares
            if isinstance(middleware, TraefikMiddleware)
        }
        if middlewares:
            data["http"]["middlewares"] = middlewares

        return ConfigFile(
            container_volume_path=static_config.get_dynamic_container_volume_path(
                self.name
            ),
            data=data,
            schema_url="https://json.schemastore.org/traefik-v3-file-provider.json",
        ).build_resource(resource_name, opts=opts, volume_resource=volume_resource)
