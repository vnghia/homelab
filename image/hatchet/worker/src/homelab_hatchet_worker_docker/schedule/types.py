from collections import defaultdict
from typing import Annotated

from homelab_pydantic import HomelabBaseModel, HomelabRootModel, Json
from pydantic import Field


class ScheduleWorkflow(HomelabBaseModel):
    id: str
    workflow: str
    input: Json | None


class NamespacedExpressionScheduleWorkflows(
    HomelabRootModel[
        defaultdict[
            str, Annotated[dict[str, ScheduleWorkflow], Field(default_factory=dict)]
        ]
    ]
):
    root: defaultdict[
        str, Annotated[dict[str, ScheduleWorkflow], Field(default_factory=dict)]
    ] = defaultdict(dict)
