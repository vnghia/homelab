from pydantic import BaseModel, PositiveInt

from .params import DaguDagParamsModel
from .step import DaguDagStepModel


class DaguDagModel(BaseModel):
    steps: list[DaguDagStepModel]

    name: str | None = None
    group: str | None = None
    tags: list[str] = []
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None
    params: DaguDagParamsModel | None = None
