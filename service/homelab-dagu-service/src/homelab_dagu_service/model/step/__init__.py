import typing
from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import Input

from .command import DaguDagStepCommandModel
from .executor import DaguDagStepExecutorModel

if typing.TYPE_CHECKING:
    from ..params import DaguDagParamsModel


class DaguDagStepModel(HomelabBaseModel):
    name: str
    command: list[DaguDagStepCommandModel]
    executor: DaguDagStepExecutorModel | None = None

    def to_step[T](
        self,
        params: "DaguDagParamsModel | None",
        main_service: ServiceResourceBase[T],
        build_args: ContainerModelBuildArgs | None,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return {
            "name": self.name,
            "command": " ".join(command.to_str(params) for command in self.command),
            "executor": self.executor.to_executor(main_service, build_args, dotenvs)
            if self.executor
            else None,
        }
