import typing
from typing import Any

from pulumi import Input
from pydantic import BaseModel

from .command import DaguDagStepCommandModel
from .executor import DaguDagStepExecutorModel

if typing.TYPE_CHECKING:
    from ... import DaguService
    from ..params import DaguDagParamsModel


class DaguDagStepModel(BaseModel):
    name: str
    command: list[DaguDagStepCommandModel]
    executor: DaguDagStepExecutorModel | None = None

    def to_step(
        self, params: "DaguDagParamsModel | None", dagu_service: "DaguService"
    ) -> dict[str, Input[Any]]:
        return {
            "name": self.name,
            "command": " ".join(command.to_str(params) for command in self.command),
            "executor": self.executor.to_executor(dagu_service)
            if self.executor
            else None,
        }
