from homelab_docker.file import File
from homelab_docker.file.config import ConfigFile
from pulumi import ResourceOptions
from pydantic import BaseModel, ConfigDict, PositiveInt

from homelab import config
from homelab.docker.resource import Resource
from homelab.docker.service.traefik import Traefik


class HttpDynamic(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    public: bool
    hostname: str | None = None
    prefix: str | None = None

    rules: list[str] = []

    container: str | None = None
    port: PositiveInt

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
        container = self.container or self.name
        resource.containers[container]

        return ConfigFile(
            volume_path=static.get_dynamic_volume_path(self.name),
            data={
                "http": {
                    "routers": {
                        self.name: {
                            "service": self.name,
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
                        }
                    },
                    "services": {
                        self.name: {
                            "loadBalancer": {
                                "servers": [
                                    {"url": "http://{}:{}".format(container, self.port)}
                                ]
                            }
                        }
                    },
                }
            },
            schema_url="https://json.schemastore.org/traefik-v3-file-provider.json",
        ).build_resource(
            resource_name, resource=resource.to_docker_resource(), opts=opts
        )
