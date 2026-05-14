from collections import defaultdict

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import (
    ServiceResourceBase,
    ServiceWithConfigResourceBase,
)
from homelab_extra_service import ExtraService
from homelab_hatchet_config import HatchetServiceConfig, HatchetServiceConfigBase
from homelab_hatchet_tool.config import Config as HatchetToolConfig
from pulumi import ResourceOptions

from .config import HatchetConfig


class HatchetService(ExtraService[HatchetConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[HatchetConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.build(None)

        self.docker_container_creation_resources: dict[str, set[str | None]] = (
            defaultdict(set)
        )
        self.docker_container_service_name_resources: dict[str, set[str | None]] = (
            defaultdict(set)
        )

        self.workder_model = self.containers[self.config.worker].model
        self.workder_extractor_args = self.extractor_args.with_container(
            self.workder_model
        )
        self.workflow_dir_volume_path = GlobalExtractor(
            self.config.workflow_dir
        ).extract_volume_path(self.workder_extractor_args)
        self.docker_dir_volume_path = GlobalExtractor(
            self.config.docker_dir
        ).extract_volume_path(self.workder_extractor_args)
        self.schedule_dir_volume_path = GlobalExtractor(
            self.config.schedule_dir
        ).extract_volume_path(self.workder_extractor_args)
        self.config_dir_volume_path = GlobalExtractor(
            self.config.config_dir
        ).extract_volume_path(self.workder_extractor_args)

    def get_workflow_volume_path(self, name: str) -> ContainerVolumePath:
        return (self.workflow_dir_volume_path / name).with_suffix(".py")

    def get_docker_model_volume_path(
        self, service: str, name: str | None
    ) -> ContainerVolumePath:
        return (
            self.docker_dir_volume_path
            / HatchetToolConfig.DOCKER_MODEL_PREFIX
            / service
            / (name or service)
        )

    def get_docker_exec_volume_path(
        self, service: str, name: str | None
    ) -> ContainerVolumePath:
        return (
            self.docker_dir_volume_path
            / HatchetToolConfig.DOCKER_EXEC_PREFIX
            / service
            / (name or service)
        )

    def get_docker_name_volume_path(self, service: str) -> ContainerVolumePath:
        return (
            self.docker_dir_volume_path / HatchetToolConfig.DOCKER_NAME_PREFIX / service
        )

    def get_schedule_volume_path(self, name: str) -> ContainerVolumePath:
        return self.schedule_dir_volume_path / name

    def get_config_volume_path(
        self, service: str, name: str | None
    ) -> ContainerVolumePath:
        return self.config_dir_volume_path / service / (name or service)

    @classmethod
    def get_service_config(
        cls, service: ServiceResourceBase
    ) -> HatchetServiceConfig | None:
        if (
            isinstance(service, ServiceWithConfigResourceBase)
            and isinstance(service.config, HatchetServiceConfigBase)
            and service.config.hatchet
        ):
            return service.config.hatchet
        return None
