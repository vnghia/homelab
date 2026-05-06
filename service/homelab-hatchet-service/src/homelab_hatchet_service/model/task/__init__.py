import ast
import typing

from homelab_docker.extract import ExtractorArgs
from homelab_hatchet_config.model.task import HatchetTaskModel
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from ... import tool
from .docker import HatchetTaskDockerModelBuilder

if typing.TYPE_CHECKING:
    from ... import HatchetService


class HatchetTaskModelBuilder(HomelabRootModel[HatchetTaskModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef:
        root = self.root.root
        function_def = HatchetTaskDockerModelBuilder(root).build_resources(
            opts, hatchet_service, extractor_args
        )

        if root.schedules:
            tool.ast.add_keyword(
                function_def,
                ast.keyword(
                    "on_crons",
                    ast.List(
                        elts=[
                            ast.Constant(value=schedule) for schedule in root.schedules
                        ]
                    ),
                ),
            )

        return function_def
