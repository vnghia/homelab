from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabRootModel

from ...params import DaguDagParamsModel
from .command import DaguDagStepRunCommandModel
from .subdag import DaguDagStepRunSubdagModel

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunModel(
    HomelabRootModel[DaguDagStepRunCommandModel | DaguDagStepRunSubdagModel]
):
    def to_run(
        self,
        dagu_service: DaguService,
        params: DaguDagParamsModel,
    ) -> dict[str, Any]:
        return self.root.to_run(dagu_service, params)
