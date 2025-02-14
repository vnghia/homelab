from typing import Any

import pulumi_docker as docker
from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.resource.file.config import ConfigFileResource
from homelab_docker.resource.volume import VolumeResource
from pulumi import ResourceOptions
from pydantic import BaseModel, HttpUrl

from ..static import TraefikStaticConfig
from .middleware import TraefikDynamicMiddlewareConfig
from .service import TraefikDynamicServiceConfig, TraefikDynamicServiceType


class TraefikHttpDynamicConfig(BaseModel):
    name: str
    public: bool
    hostname: str | None = None
    prefix: str | None = None

    rules: list[str] = []
    service: TraefikDynamicServiceConfig
    middlewares: list[TraefikDynamicMiddlewareConfig] = []

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        volume_resource: VolumeResource,
        containers: dict[str, docker.Container],
        static_config: TraefikStaticConfig,
    ) -> ConfigFileResource:
        entrypoint = static_config.service_config.entrypoint
        hostname = (
            static_config.network_resource.public.hostnames
            if self.public
            else static_config.network_resource.private.hostnames
        )[self.hostname or self.name]

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    self.name: {
                        "service": self.service.to_service_name(self.name),
                        "entryPoints": [
                            entrypoint.public_https
                            if self.public
                            else entrypoint.private_https
                        ],
                        "rule": hostname.apply(
                            lambda x: " && ".join(
                                ["Host(`{}`)".format(x)]
                                + (
                                    ["PathPrefix(`{}`)".format(self.prefix)]
                                    if self.prefix
                                    else []
                                )
                                + self.rules
                            )
                        ),
                        "middlewares": [
                            middleware.name for middleware in self.middlewares
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

        service_full = self.service.full
        if service_full:
            data["http"]["services"] = service_full.to_http_service(
                TraefikDynamicServiceType.HTTP, self.name, containers
            )

        middlewares = {
            middleware.name: middleware.data
            for middleware in self.middlewares
            if middleware.data is not None
        }
        if middlewares:
            data["http"]["middlewares"] = middlewares

        return ConfigFileModel(
            container_volume_path=static_config.get_dynamic_container_volume_path(
                self.name
            ),
            data=data,
            schema_url=HttpUrl(
                "https://json.schemastore.org/traefik-v3-file-provider.json"
            ),
        ).build_resource(resource_name, opts=opts, volume_resource=volume_resource)
