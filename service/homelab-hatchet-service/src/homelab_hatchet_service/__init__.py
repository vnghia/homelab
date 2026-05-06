from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_extra_service import ExtraService
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

        self.workflow_dir_volume_path = GlobalExtractor(
            self.config.workflow_dir
        ).extract_volume_path(self.extractor_args)
        self.docker_dir_volume_path = GlobalExtractor(
            self.config.docker_dir
        ).extract_volume_path(self.extractor_args)
