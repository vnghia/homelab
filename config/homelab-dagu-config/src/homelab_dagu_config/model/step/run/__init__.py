from __future__ import annotations

from homelab_pydantic import HomelabRootModel

from .command import DaguDagStepRunCommandModel
from .subdag import DaguDagStepRunSubdagModel


class DaguDagStepRunModel(
    HomelabRootModel[DaguDagStepRunCommandModel | DaguDagStepRunSubdagModel]
):
    pass
