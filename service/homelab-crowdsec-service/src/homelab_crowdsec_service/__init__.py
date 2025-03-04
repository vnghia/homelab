from __future__ import annotations

from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    YamlDumper,
)
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

from .config import CrowdsecConfig


class DockerAcquisConfigResource(
    ConfigFileResource[JsonDefaultModel], module="crowdsec", name="AcquisConfig"
):
    validator = JsonDefaultModel
    dumper = YamlDumper

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        crowdsec_service: CrowdsecService,
    ):
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=crowdsec_service.config.docker.acquis_dir.extract_volume_path(
                crowdsec_service, None
            )
            / "docker",
            data={
                "source": "docker",
                "use_container_labels": True,
                "check_interval": crowdsec_service.config.docker.check_interval,
            },
            volume_resource=crowdsec_service.docker_resource_args.volume,
        )


class CrowdsecService(ServiceWithConfigResourceBase[CrowdsecConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[CrowdsecConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.docker = DockerAcquisConfigResource(
            "docker", opts=self.child_opts, crowdsec_service=self
        )
        self.options[None].files = [self.docker]
        self.build_containers()

        self.register_outputs({})
