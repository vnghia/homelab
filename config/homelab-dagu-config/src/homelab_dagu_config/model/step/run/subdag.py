from __future__ import annotations

from homelab_pydantic import HomelabBaseModel

from ...params import DaguDagParamsModel


class DaguDagStepRunSubdagModel(HomelabBaseModel):
    service: str
    dag: str
    params: DaguDagParamsModel = DaguDagParamsModel()
