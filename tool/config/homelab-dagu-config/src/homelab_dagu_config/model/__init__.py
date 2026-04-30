from __future__ import annotations

from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from .params import DaguDagParamsModel
from .step import DaguDagStepModel


class DaguDagModel(HomelabBaseModel):
    dotenvs: list[str | None] = []
    name: str | None = None
    path: str | None = None

    group: str | None = None
    tags: list[str] = []
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None
    params: DaguDagParamsModel = DaguDagParamsModel()

    steps: list[DaguDagStepModel] = []
