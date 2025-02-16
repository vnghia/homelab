import typing
from typing import Any

from homelab_docker.resource.service import ServiceResourceArgs
from pulumi import Input
from pydantic import BaseModel

from .command import DaguDagStepCommandModel
from .executor import DaguDagStepExecutorModel

if typing.TYPE_CHECKING:
    from ..params import DaguDagParamsModel


class DaguDagStepModel(BaseModel):
    name: str
    command: list[DaguDagStepCommandModel]
    executor: DaguDagStepExecutorModel | None = None

    def to_step(
        self, params: "DaguDagParamsModel", service_resource_args: ServiceResourceArgs
    ) -> dict[str, Input[Any]]:
        return {
            "name": self.name,
            "command": " ".join(command.to_str(params) for command in self.command),
        } | (
            {"executor": self.executor.to_executor(service_resource_args)}
            if self.executor
            else {}
        )
