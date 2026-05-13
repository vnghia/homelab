from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.config import ConfigFileResource, JsonDumper
from homelab_hatchet_config import HatchetServiceConfig
from homelab_hatchet_config.model.task.docker import HatchetTaskDockerExecInnerModel
from homelab_pydantic import docker as schema
from pulumi import ResourceOptions

from homelab_hatchet_service import HatchetService


class HatchetDockerContainerExecModelResource(
    ConfigFileResource[schema.ContainerExecModel],
    module="hatchet",
    name="ContainerExec",
):
    validator = schema.ContainerExecModel
    dumper = JsonDumper[schema.ContainerExecModel]

    def __init__(
        self,
        resource_name: str | None,
        model: HatchetTaskDockerExecInnerModel,
        *,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        resource_name = resource_name or extractor_args.service.name()
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=hatchet_service.get_docker_exec_volume_path(
                extractor_args.service.name(), resource_name
            ),
            data={
                "container": model.container,
                "command": model.build_command(extractor_args),
            },
            permission=hatchet_service.user,
            extractor_args=hatchet_service.extractor_args,
        )


class HatchetDockerContainerServiceNameResource(
    ConfigFileResource[schema.ContainerServiceName],
    module="hatchet",
    name="ContainerServiceName",
):
    validator = schema.ContainerServiceName
    dumper = JsonDumper[schema.ContainerServiceName]

    def __init__(
        self,
        config: HatchetServiceConfig,
        *,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        service = extractor_args.service

        if containers := (
            hatchet_service.docker_container_service_name_resources[service.name()]
            | config.docker.names
        ):
            super().__init__(
                service.name(),
                opts=opts,
                volume_path=hatchet_service.get_docker_name_volume_path(service.name()),
                data={
                    (key or schema.ContainerServiceName.NONE_KEY): service.containers[
                        key
                    ].resource.name
                    for key in containers
                },
                permission=hatchet_service.user,
                extractor_args=hatchet_service.extractor_args,
            )
