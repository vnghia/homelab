import ast
import copy
import typing
from pathlib import Path
from typing import ClassVar

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.docker import DockerContainerCreationModelResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_hatchet_config.model.task.docker import (
    HatchetTaskDockerExecModel,
    HatchetTaskDockerModel,
    HatchetTaskDockerRunModel,
)
from homelab_hatchet_config.model.task.schedule import HatchetTaskWorkflowInputArgs
from homelab_hatchet_tool.docker import Docker
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .... import tool

if typing.TYPE_CHECKING:
    from .... import HatchetService

TEMPLATE_PATH = Path(__file__).parent / "template.py"
TEMPLATE = ast.parse(TEMPLATE_PATH.read_text())

SERVICE_PLACEHOLDER = "#service"
CONTAINER_PLACEHOLDER = "#container"
NAME_PLACEHOLDER = "#name"


def replace_placeholder(
    template_name: str,
    service: ServiceResourceBase,
    container: str | None,
    name: str | None,
) -> ast.AsyncFunctionDef:
    function_def = copy.deepcopy(
        tool.ast.find(TEMPLATE, ast.AsyncFunctionDef, template_name)
    )

    task_name = service.add_service_name(container)
    function_name = task_name.replace("-", "_")
    service_name = service.name()

    function_def.name = function_name

    tool.ast.add_keyword(
        function_def, ast.keyword(arg="name", value=ast.Constant(value=task_name))
    )

    for stmt in function_def.body:
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value == SERVICE_PLACEHOLDER:
                stmt.value.value = service_name
            elif stmt.value.value == CONTAINER_PLACEHOLDER:
                stmt.value.value = container
            elif stmt.value.value == NAME_PLACEHOLDER:
                stmt.value.value = name

    return function_def


class HatchetTaskDockerRunModelBuilder(HomelabRootModel[HatchetTaskDockerRunModel]):
    TEMPLATE_NAME: ClassVar[str] = "run"

    def build_resources(
        self,
        opts: ResourceOptions,
        workflow: bool,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef | HatchetTaskWorkflowInputArgs:
        root = self.root.run
        service = extractor_args.service

        if not hatchet_service.docker_container_creation_resources[service.name()].get(
            root.container, None
        ):
            hatchet_service.docker_container_creation_resources[service.name()][
                root.container
            ] = DockerContainerCreationModelResource(
                root.container,
                opts=opts,
                volume_path=hatchet_service.get_docker_run_volume_path(
                    service.name(), root.container
                ),
                permission=hatchet_service.user,
                extractor_args=extractor_args,
            )

        if workflow:
            if root.command or root.entrypoint:
                raise ValueError(
                    "Docker task workflow builder only supports service, container and name"
                )
            return replace_placeholder(
                self.TEMPLATE_NAME, service, root.container, root.name
            )

        return HatchetTaskWorkflowInputArgs(
            workflow=Docker.DOCKER_RUN_TASK,
            input={"service": service.name(), "container": root.container}
            | (
                {"command": command}
                if (command := root.build_command(extractor_args))
                else {}
            )
            | (
                {"entrypoint": entrypoint}
                if (entrypoint := root.build_entrypoint(extractor_args))
                else {}
            ),
        )


class HatchetTaskDockerExecModelBuilder(HomelabRootModel[HatchetTaskDockerExecModel]):
    TEMPLATE_NAME: ClassVar[str] = "exec"

    def build_resources(
        self,
        opts: ResourceOptions,
        workflow: bool,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef:
        root = self.root.exec
        return replace_placeholder(
            self.TEMPLATE_NAME, extractor_args.service, root.container, None
        )


class HatchetTaskDockerModelBuilder(HomelabRootModel[HatchetTaskDockerModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef | HatchetTaskWorkflowInputArgs:
        root = self.root
        return (
            HatchetTaskDockerRunModelBuilder(root.docker)
            if isinstance(root.docker, HatchetTaskDockerRunModel)
            else HatchetTaskDockerExecModelBuilder(root.docker)
        ).build_resources(opts, root.should_workflow, hatchet_service, extractor_args)
