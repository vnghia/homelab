import ast
import copy
import typing
from pathlib import Path
from typing import ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_hatchet_config import HatchetServiceConfig
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from ..tool import find_ast
from .task import HatchetTaskModelBuilder

if typing.TYPE_CHECKING:
    from .. import HatchetService

TEMPLATE_PATH = Path(__file__).parent / "template.py"
TEMPLATE = ast.parse(TEMPLATE_PATH.read_text())


class HatchetServiceBuilder(HomelabRootModel[HatchetServiceConfig]):
    TEMPLATE_NAME: ClassVar[str] = "build_workflows"

    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        from ..resource import HatchetWorkflowResource

        tasks = [
            HatchetTaskModelBuilder(task_model).build_resources(
                opts, hatchet_service, extractor_args
            )
            for task_model in self.root.task.root.values()
        ]

        workflow = copy.deepcopy(TEMPLATE)
        function_def = find_ast(workflow, ast.FunctionDef, self.TEMPLATE_NAME)
        function_def.body = [
            *tasks,
            ast.Return(ast.List(elts=[ast.Name(id=task.name) for task in tasks])),
        ]

        HatchetWorkflowResource(
            None,
            content=ast.unparse(workflow),
            opts=opts,
            hatchet_service=hatchet_service,
            extractor_args=extractor_args,
        )
