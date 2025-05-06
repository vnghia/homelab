from __future__ import annotations

from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    TomlDumper,
)
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import FrpConfig


class FrpClientConfigResource(
    ConfigFileResource[JsonDefaultModel], module="frp", name="ClientConfig"
):
    validator = JsonDefaultModel
    dumper = TomlDumper

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        frp_service: FrpService,
    ) -> None:
        config = frp_service.config
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=GlobalExtractor(config.path).extract_volume_path(
                frp_service, None
            ),
            data={
                "serverAddr": str(config.server.addr),
                "serverPort": config.server.port,
                "log": {"to": "console"},
                "auth": {"method": "token", "token": config.server.token},
                "transport": {
                    "protocol": config.protocol,
                    "tls": {"enable": False},
                    "poolCount": config.pool,
                },
            },
            volume_resource=frp_service.docker_resource_args.volume,
        )


class FrpService(ServiceWithConfigResourceBase[FrpConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[FrpConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.client_config = FrpClientConfigResource(
            "client=config", opts=self.child_opts, frp_service=self
        )
        self.options[None].files = [self.client_config]
        self.build_containers()

        self.register_outputs({})
