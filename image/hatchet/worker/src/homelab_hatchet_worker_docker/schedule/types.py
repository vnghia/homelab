from collections import defaultdict
from typing import Annotated

from hatchet_sdk.utils.typing import JSONSerializableMapping
from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pydantic import Field


class ScheduleWorkflow(HomelabBaseModel):
    id: str
    workflow: str
    input: JSONSerializableMapping | None


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
