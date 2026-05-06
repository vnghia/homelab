import typing

from homelab_docker.extract import ExtractorArgs
from homelab_hatchet_config.model.task import HatchetTaskModel
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .docker import HatchetTaskDockerModelBuilder

if typing.TYPE_CHECKING:
    from ... import HatchetService


class HatchetTaskModelBuilder(HomelabRootModel[HatchetTaskModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        root = self.root.root
        HatchetTaskDockerModelBuilder(root).build_resources(
            opts, hatchet_service, extractor_args
        )
