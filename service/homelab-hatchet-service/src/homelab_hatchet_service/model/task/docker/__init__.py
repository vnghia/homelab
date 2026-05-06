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
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .... import tool

if typing.TYPE_CHECKING:
    from .... import HatchetService

TEMPLATE_PATH = Path(__file__).parent / "template.py"
TEMPLATE = ast.parse(TEMPLATE_PATH.read_text())

TASK_NAME_PLACEHOLDER = "#task-name"
SERVICE_PLACEHOLDER = "#service"
NAME_PLACEHOLDER = "#name"


def replace_placeholder(
    template_name: str,
    service: ServiceResourceBase,
    name: str | None,
) -> ast.AsyncFunctionDef:
    function_def = copy.deepcopy(
        tool.ast.find(TEMPLATE, ast.AsyncFunctionDef, template_name)
    )

    task_name = service.add_service_name(name)
    function_name = task_name.replace("-", "_")
    service_name = service.name()

    function_def.name = function_name

    tool.ast.add_keyword(
        function_def,
        ast.keyword(
            arg="name",
            value=ast.Call(
                func=ast.Attribute(
                    value=ast.Constant(value="{{}}-{}".format(task_name)), attr="format"
                ),
                args=[
                    ast.Attribute(
                        value=ast.Call(
                            func=ast.Attribute(
                                value=ast.Name(id="Config"), attr="load"
                            ),
                            args=[],
                        ),
                        attr="host",
                    )
                ],
            ),
        ),
    )

    for stmt in function_def.body:
        if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Constant):
            if stmt.value.value == SERVICE_PLACEHOLDER:
                stmt.value.value = service_name
            elif stmt.value.value == NAME_PLACEHOLDER:
                stmt.value.value = name

    return function_def


class HatchetTaskDockerRunModelBuilder(HomelabRootModel[HatchetTaskDockerRunModel]):
    TEMPLATE_NAME: ClassVar[str] = "run"

    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef:
        root = self.root.run
        service = extractor_args.service
        DockerContainerCreationModelResource(
            root,
            opts=opts,
            volume_path=hatchet_service.get_docker_run_volume_path(
                service.name(), root.model
            ),
            permission=hatchet_service.user,
            extractor_args=extractor_args,
        )

        return replace_placeholder(self.TEMPLATE_NAME, service, root.model)


class HatchetTaskDockerExecModelBuilder(HomelabRootModel[HatchetTaskDockerExecModel]):
    TEMPLATE_NAME: ClassVar[str] = "exec"

    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef:
        root = self.root.exec
        return replace_placeholder(
            self.TEMPLATE_NAME, extractor_args.service, root.model
        )


class HatchetTaskDockerModelBuilder(HomelabRootModel[HatchetTaskDockerModel]):
    def build_resources(
        self,
        opts: ResourceOptions,
        hatchet_service: HatchetService,
        extractor_args: ExtractorArgs,
    ) -> ast.AsyncFunctionDef:
        root = self.root
        return (
            HatchetTaskDockerRunModelBuilder(root.docker)
            if isinstance(root.docker, HatchetTaskDockerRunModel)
            else HatchetTaskDockerExecModelBuilder(root.docker)
        ).build_resources(opts, hatchet_service, extractor_args)
