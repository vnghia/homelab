from __future__ import annotations

from typing import ClassVar

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ...params import DaguDagParamsModel


class DaguDagStepRunSubdagParallelModel(HomelabBaseModel):
    PARAM_KEY: ClassVar[str] = "${ITEM}"

    items: list[GlobalExtract]
    max_concurrent: PositiveInt | None = None


class DaguDagStepRunSubdagModel(HomelabBaseModel):
    service: str
    dag: str
    params: DaguDagParamsModel = DaguDagParamsModel()
    parallel: DaguDagStepRunSubdagParallelModel | None = None
