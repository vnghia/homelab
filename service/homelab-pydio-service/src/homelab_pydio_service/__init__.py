from __future__ import annotations

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.extract.service import ServiceExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    YamlDumper,
)
from homelab_extra_service import ExtraService
from pulumi import ResourceOptions

from homelab_pydio_service.config import PydioConfig


class PydioInstallConfigResource(
    ConfigFileResource[JsonDefaultModel], module="pydio", name="config"
):
    validator = JsonDefaultModel
    dumper = YamlDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        config: PydioConfig,
        pydio_service: PydioService,
    ) -> None:
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=ServiceExtractor(config.install_path).extract_volume_path(
                pydio_service, None
            ),
            data=GlobalExtractor.extract_recursively(
                config.install, pydio_service, None
            ),
            volume_resource=pydio_service.docker_resource_args.volume,
        )


class PydioService(ExtraService[PydioConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[PydioConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
        self.options[None].files = [
            PydioInstallConfigResource(
                "install", opts=self.child_opts, config=self.config, pydio_service=self
            )
        ]
        self.build()
