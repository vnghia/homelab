import dataclasses
from pathlib import PosixPath
from typing import Any, ClassVar

from homelab_docker.model.file.config import ConfigFile
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.volume import VolumeResource
from pulumi import ResourceOptions
from pydantic import PositiveInt

from homelab_dagu_service import DaguService


@dataclasses.dataclass
class DaguDagStep:
    name: str
    command: str
    executor: dict[str, Any] | None = None

    def dict(self) -> dict[str, Any]:
        return {"name": self.name, "command": self.command, "executor": self.executor}


@dataclasses.dataclass
class DaguDag:
    DAGS_DIR_ENV: ClassVar[str] = "DAGU_DAGS_DIR"
    steps: list[DaguDagStep]

    name: str | None = None
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        dagu_service: DaguService,
        volume_resource: VolumeResource,
    ) -> FileResource:
        return ConfigFile(
            container_volume_path=dagu_service.model.container.envs[self.DAGS_DIR_ENV]
            .as_container_volume_path()
            .join(PosixPath(self.name or resource_name), ".yaml"),
            data={
                "steps": [step.dict() for step in self.steps],
            }
            | ({"schedule": self.schedule} if self.schedule else {})
            | ({"maxActiveRuns": self.max_active_runs} if self.max_active_runs else {}),
            schema_url="https://raw.githubusercontent.com/dagu-org/dagu/refs/heads/main/schemas/dag.schema.json",
        ).build_resource(resource_name, opts=opts, volume_resource=volume_resource)
