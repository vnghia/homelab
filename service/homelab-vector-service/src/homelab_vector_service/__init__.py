from collections import defaultdict

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.observability import (
    ContainerObservabilityInputModel,
)
from homelab_docker.model.docker.container.volume_path import ContainerVolumePath
from homelab_docker.model.host import HostNoServiceModel
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extra_service import ExtraService
from pulumi import ResourceOptions

from .config import VectorConfig
from .resource import VectorConfigData, VectorConfigResource


class VectorService(ExtraService[VectorConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[VectorConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.config_dir = GlobalExtractor(self.config.dir).extract_volume_path(
            self.extractor_args
        )
        self.configs: dict[str, dict[str | None, VectorConfigResource]] = defaultdict(
            dict
        )

        self.build(None)

    def get_config_path(self, config_key: str) -> ContainerVolumePath:
        return self.config_dir / config_key

    def build_observability(
        self, opts: ResourceOptions, service: ServiceResourceBase, container: str | None
    ) -> None:
        container_resource = service.containers[container]
        config = container_resource.model.observability
        if not config:
            return

        extractor_args = service.extractor_args.with_container(container_resource)
        prefix = service.container_full_names[container]
        keys: dict[str, str] = {}

        def build_input(input: ContainerObservabilityInputModel) -> str:
            if not input.service and not input.has_container:
                return keys[input.input]
            service_name = input.service if input.service else service.name()
            return self.configs[service_name][input.container].keys[input.input]

        sources = {}
        for key, data in config.sources.items():
            full_key = HostNoServiceModel.add_prefix(prefix, key)
            keys[key] = full_key
            sources[full_key] = {
                "type": data.type
            } | GlobalExtractor.extract_recursively(data.model_extra, extractor_args)

        transforms = {}
        for key, data in config.transforms.items():
            inputs = [build_input(input) for input in data.inputs]
            if not inputs:
                continue
            full_key = HostNoServiceModel.add_prefix(prefix, key)
            keys[key] = full_key
            transforms[full_key] = {
                "type": data.type,
                "inputs": inputs,
            } | GlobalExtractor.extract_recursively(data.model_extra, extractor_args)

        sinks = {}
        for key, data in config.sinks.items():
            inputs = [build_input(input) for input in data.inputs]
            if not inputs:
                continue
            sinks[HostNoServiceModel.add_prefix(prefix, key)] = {
                "type": data.type,
                "inputs": inputs,
            } | GlobalExtractor.extract_recursively(data.model_extra, extractor_args)

        self.configs[service.name()][container] = VectorConfigResource(
            container or service.name(),
            opts=opts,
            config_data=VectorConfigData(
                keys=keys, sources=sources, transforms=transforms, sinks=sinks
            ),
            vector_service=self,
        )
