import types
from typing import Self

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import Output, ResourceOptions

from .config import ExtraConfig


class ExtraService[T: ExtraConfig](ServiceWithConfigResourceBase[T]):
    REGISTER_OUTPUT = True

    def __init__(
        self,
        model: ServiceWithConfigModel[T],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

    def extract_variable_str(self, variable: str) -> Output[str]:
        return GlobalExtractor(self.model.variables[variable]).extract_str(
            self.extractor_args
        )

    def extract_variable_volume_path(self, variable: str) -> ContainerVolumePath:
        return GlobalExtractor(self.model.variables[variable]).extract_volume_path(
            self.extractor_args
        )

    def build(self, hook_module: types.ModuleType | None) -> Self:
        if hook_module:
            hook_module.pre_build(self)
        self.build_containers()
        if hook_module:
            hook_module.post_build(self)

        if self.REGISTER_OUTPUT:
            self.register_outputs({})

        return self
