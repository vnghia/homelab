from typing import Any

from homelab_docker.resource.service import ServiceResourceArgs
from pulumi import Input
from pydantic import BaseModel

from .executor import DaguDagExecutorModel


class DaguDagStepModel(BaseModel):
    name: str
    command: list[str]
    executor: DaguDagExecutorModel | None = None

    def to_step(
        self, service_resource_args: ServiceResourceArgs
    ) -> dict[str, Input[Any]]:
        return {"name": self.name, "command": self.command} | (
            {"executor": self.executor.to_executor(service_resource_args)}
            if self.executor
            else {}
        )
