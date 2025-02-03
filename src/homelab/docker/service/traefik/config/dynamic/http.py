from typing import Any

import homelab_config as config
from homelab_docker.file import File
from homelab_docker.file.config import ConfigFile
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, PositiveInt

from homelab.docker.resource import Resource
from homelab.docker.service.traefik import Traefik
from homelab.docker.service.traefik.config.dynamic.middleware import Middleware
from homelab.docker.service.traefik.config.dynamic.service import Service, ServiceType


class HttpDynamic(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    public: bool
    hostname: str | None = None
    prefix: str | None = None

    rules: list[str] = []

    service: Service | PositiveInt | str

    middlewares: list[Middleware | str] = []

    def build_resource(
        self,
        resource_name: str,
        resource: Resource,
        traefik: Traefik,
        opts: ResourceOptions | None = None,
    ) -> File:
        static = traefik.static
        entrypoint = static.service_config.entrypoint
        dns = config.network.dns
        host = (dns.public.hostnames if self.public else dns.private.hostnames)[
            self.hostname or self.name
        ]

        data: dict[str, Any] = {
            "http": {
                "routers": {
                    self.name: {
                        "service": self.name
                        if isinstance(self.service, (Service, int))
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
                            if isinstance(middleware, Middleware)
                            else middleware
                            for middleware in self.middlewares
                        ],
                        "tls": {
                            "certResolver": static.PUBLIC_CERT_RESOLVER
                            if self.public
                            else static.PRIVATE_CERT_RESOLVER
                        },
                    }
                },
            }
        }

        if isinstance(self.service, Service):
            data["http"]["services"] = {
                self.name: {
                    "loadBalancer": {
                        "servers": [
                            {
                                "url": str(
                                    self.service.to_url(
                                        ServiceType.HTTP, self.name, resource
                                    )
                                )
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
                                "url": str(
                                    Service(port=self.service).to_url(
                                        ServiceType.HTTP, self.name, resource
                                    )
                                )
                            }
                        ]
                    }
                }
            }

        middlewares = {
            middleware.name: middleware.data
            for middleware in self.middlewares
            if isinstance(middleware, Middleware)
        }
        if middlewares:
            data["http"]["middlewares"] = middlewares

        return ConfigFile(
            volume_path=static.get_dynamic_volume_path(self.name),
            data=data,
            schema_url="https://json.schemastore.org/traefik-v3-file-provider.json",
        ).build_resource(
            resource_name, resource=resource.to_docker_resource(), opts=opts
        )
