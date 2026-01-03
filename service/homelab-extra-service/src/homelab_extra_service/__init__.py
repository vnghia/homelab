from typing import Self

from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from pulumi import ResourceOptions

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

    def build(self) -> Self:
        self.build_containers()

        if self.REGISTER_OUTPUT:
            self.register_outputs({})

        return self
