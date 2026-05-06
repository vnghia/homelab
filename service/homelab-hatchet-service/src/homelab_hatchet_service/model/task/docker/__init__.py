import typing

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.docker import DockerContainerCreationModelResource
from homelab_hatchet_config.model.task.docker import (
    HatchetTaskDockerExecModel,
    HatchetTaskDockerModel,
    HatchetTaskDockerRunModel,
)
from homelab_hatchet_tool.config import Config
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from .... import HatchetService


class HatchetTaskDockerRunModelBuilder(HomelabRootModel[HatchetTaskDockerRunModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        root = self.root.run
        DockerContainerCreationModelResource(
            root,
            opts=opts,
            volume_path=hatchet_service.docker_dir_volume_path
            / Config.DOCKER_RUN_PREFIX
            / extractor_args.service.name()
            / (root.model or extractor_args.service.name()),
            permission=hatchet_service.user,
            extractor_args=extractor_args,
        )


class HatchetTaskDockerExecModelBuilder(HomelabRootModel[HatchetTaskDockerExecModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        pass


class HatchetTaskDockerModelBuilder(HomelabRootModel[HatchetTaskDockerModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        root = self.root.docker
        (
            HatchetTaskDockerRunModelBuilder(root)
            if isinstance(root, HatchetTaskDockerRunModel)
            else HatchetTaskDockerExecModelBuilder(root)
        ).build_resources(opts, hatchet_service, extractor_args)
