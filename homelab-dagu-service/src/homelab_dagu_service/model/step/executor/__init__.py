import typing
from typing import Any

from pulumi import Input
from pydantic import RootModel

from .docker import DaguDagStepDockerExecutorModel

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepExecutorModel(RootModel[DaguDagStepDockerExecutorModel]):
    root: DaguDagStepDockerExecutorModel

    def to_executor(self, dagu_service: "DaguService") -> dict[str, Input[Any]]:
        return self.root.to_executor(dagu_service)
