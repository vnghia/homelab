import typing
from typing import Any

from pulumi import Input
from pydantic import RootModel

from .exec import DaguDagStepDockerExecutorExecModel

if typing.TYPE_CHECKING:
    from ..... import DaguService


class DaguDagStepDockerExecutorModel(RootModel[DaguDagStepDockerExecutorExecModel]):
    root: DaguDagStepDockerExecutorExecModel

    def to_executor(self, dagu_service: "DaguService") -> dict[str, Input[Any]]:
        return {"type": "docker", "config": self.root.to_executor_config(dagu_service)}
