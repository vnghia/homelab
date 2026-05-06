import typing

from homelab_docker.extract import ExtractorArgs
from homelab_hatchet_config import HatchetServiceConfig
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .task import HatchetTaskModelBuilder

if typing.TYPE_CHECKING:
    from .. import HatchetService


class HatchetServiceBuilder(HomelabRootModel[HatchetServiceConfig]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        for task_model in self.root.task.root.values():
            HatchetTaskModelBuilder(task_model).build_resources(
                opts, hatchet_service, extractor_args
            )
