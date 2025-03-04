from __future__ import annotations

from homelab_pydantic import HomelabBaseModel

from .continue_on import DaguDagStepContinueOnModel
from .executor import DaguDagStepExecutorModel
from .run import DaguDagStepRunModel


class DaguDagStepModel(HomelabBaseModel):
    name: str
    run: DaguDagStepRunModel
    continue_on: DaguDagStepContinueOnModel | None = None
    executor: DaguDagStepExecutorModel | None = None
