import ast
import typing

from homelab_docker.extract import ExtractorArgs
from homelab_hatchet_config.model.scheduler import HatchetServiceSchedulerModel
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
        task_name: str | None,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef | HatchetServiceSchedulerModel:
        root = self.root.root
        task = HatchetTaskDockerModelBuilder(root).build_resources(
            task_name, opts, hatchet_service, extractor_args
        )

        if isinstance(task, ast.AsyncFunctionDef):
            result = task
            if root.schedules:
                tool.ast.add_keyword(
                    result,
                    ast.keyword(
                        "on_crons",
                        ast.List(
                            elts=[
                                ast.Constant(value=schedule)
                                for schedule in root.schedules
                            ]
                        ),
                    ),
                )
            return result

        return HatchetServiceSchedulerModel(
            workflow=task.workflow,
            input=task.input,
            schedules=root.schedules,
        )
