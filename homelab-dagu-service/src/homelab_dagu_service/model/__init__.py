import typing
from typing import Any

from pulumi import ResourceOptions
from pydantic import BaseModel, PositiveInt

from .params import DaguDagParamsModel
from .step import DaguDagStepModel

if typing.TYPE_CHECKING:
    from .. import DaguService
    from ..resource import DaguDagResource


class DaguDagModel(BaseModel):
    name: str | None = None
    path: str | None = None

    group: str | None = None
    tags: list[str] = []
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None
    params: DaguDagParamsModel | None = None

    steps: list[DaguDagStepModel]

    def to_data(self, dagu_service: "DaguService") -> dict[str, Any]:
        return {
            "name": self.name,
            "group": self.group,
            "tags": self.tags,
            "schedule": self.schedule,
            "maxActiveRuns": self.max_active_runs,
            "params": [{key: param} for key, param in self.params.root.items()]
            if self.params
            else None,
            "steps": [step.to_step(self.params, dagu_service) for step in self.steps],
        }

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        dagu_service: "DaguService",
    ) -> "DaguDagResource":
        from ..resource import DaguDagResource

        return DaguDagResource(
            resource_name, self, opts=opts, dagu_service=dagu_service
        )
