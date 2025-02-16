import typing
from typing import Any

from pulumi import Input
from pydantic import BaseModel

if typing.TYPE_CHECKING:
    from ..... import DaguService


class DaguDagStepDockerExecutorExecModel(BaseModel):
    container: str

    def to_executor_config(self, dagu_service: "DaguService") -> dict[str, Input[Any]]:
        return {"containerName": dagu_service.args.containers[self.container].name}
