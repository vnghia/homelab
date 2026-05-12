import ast
import copy
import typing
from pathlib import Path
from typing import ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.docker import DockerContainerCreationModelResource
from homelab_hatchet_config import HatchetServiceConfig
from homelab_pydantic import ROOT_PATH, HomelabRootModel
from pulumi import ResourceOptions

from .. import tool
from .task import HatchetTaskModelBuilder

if typing.TYPE_CHECKING:
    from .. import HatchetService

TEMPLATE_PATH = Path(__file__).parent / "template.py"
TEMPLATE = ast.parse(TEMPLATE_PATH.read_text())


class HatchetServiceBuilder(HomelabRootModel[HatchetServiceConfig]):
    TEMPLATE_NAME: ClassVar[str] = "build_workflows"

    @classmethod
    def get_workflow_dir(cls, hatchet_service: HatchetService, service: str) -> Path:
        return (
            ROOT_PATH
            / "service"
            / "homelab-{}-service".format(service)
            / "src"
            / "homelab_{}_service".format(service)
            / hatchet_service.name()
            / "workflow"
        )

    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> None:
        from ..resource import (
            HatchetScheduleResource,
            HatchetServiceConfigResource,
            HatchetWorkflowResource,
        )
        from ..resource.docker import HatchetDockerContainerServiceNameResource

        root = self.root
        service = extractor_args.service

        tasks_defs = []
        schedules = {}

        for task_name, task_model in root.task.root.items():
            result = HatchetTaskModelBuilder(task_model).build_resources(
                task_name, opts, hatchet_service, extractor_args
            )
            if isinstance(result, ast.AsyncFunctionDef):
                tasks_defs.append(result)
            else:
                schedules[task_name] = result

        for docker_container_creation in (
            hatchet_service.docker_container_creation_resources[service.name()]
            | root.docker.models
        ):
            DockerContainerCreationModelResource(
                docker_container_creation,
                opts=opts,
                volume_path=hatchet_service.get_docker_model_volume_path(
                    service.name(), docker_container_creation
                ),
                permission=hatchet_service.user,
                extractor_args=extractor_args,
            )

        workflows = {}
        if workflow_dir := self.get_workflow_dir(hatchet_service, service.name()):
            for workflow_path in workflow_dir.glob("*.py"):
                if workflow_path.name.startswith("__"):
                    continue
                with open(workflow_path) as workflow_file:
                    workflows[workflow_path.stem] = ast.parse(workflow_file.read())

        if root.config:
            HatchetServiceConfigResource(
                root.config,
                opts=opts,
                hatchet_service=hatchet_service,
                extractor_args=extractor_args,
            )

        HatchetDockerContainerServiceNameResource(
            root,
            opts=opts,
            hatchet_service=hatchet_service,
            extractor_args=extractor_args,
        )

        if tasks_defs:
            workflow = copy.deepcopy(TEMPLATE)
            function_def = tool.ast.find(workflow, ast.FunctionDef, self.TEMPLATE_NAME)
            function_def.body = [
                *tasks_defs,
                ast.Return(
                    ast.List(
                        elts=[ast.Name(id=task_def.name) for task_def in tasks_defs]
                    )
                ),
            ]

            HatchetWorkflowResource(
                None,
                content=ast.unparse(workflow),
                opts=opts,
                hatchet_service=hatchet_service,
                extractor_args=extractor_args,
            )

        if schedules:
            HatchetScheduleResource(
                None,
                schedules,
                opts=opts,
                hatchet_service=hatchet_service,
                extractor_args=extractor_args,
            )

        for workflow_name, workflow in workflows.items():
            HatchetWorkflowResource(
                workflow_name,
                content=ast.unparse(workflow),
                opts=opts,
                hatchet_service=hatchet_service,
                extractor_args=extractor_args,
            )
