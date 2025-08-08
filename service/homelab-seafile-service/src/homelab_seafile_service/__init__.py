from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_extra_service import ExtraService
from pulumi import ResourceOptions

from .config import SeafileConfig


class SeafileService(ExtraService[SeafileConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[SeafileConfig],
        *,
        opts: ResourceOptions,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)
        self.build()
