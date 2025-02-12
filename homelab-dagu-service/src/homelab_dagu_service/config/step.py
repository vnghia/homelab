import dataclasses
from typing import Any

from .executor.docker import DaguDagDockerExecutorConfig


@dataclasses.dataclass
class DaguDagStepConfig:
    name: str
    command: str
    executor: DaguDagDockerExecutorConfig | None = None

    def dict(self) -> dict[str, Any]:
        return {"name": self.name, "command": self.command} | (
            {"executor": self.executor.to_executor()} if self.executor else {}
        )
