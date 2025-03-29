from __future__ import annotations

import typing

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.command import DaguDagStepRunCommandModel
from homelab_dagu_config.model.step.script import DaguDagStepScriptModel
from homelab_pydantic.model import HomelabRootModel

from homelab_dagu_service.model.step.run.command import (
    DaguDagStepRunCommandModelBuilder,
)

if typing.TYPE_CHECKING:
    from ... import DaguService


class DaguDagStepScriptModelBuilder(HomelabRootModel[DaguDagStepScriptModel]):
    def to_script(self, _dagu_service: DaguService, params: DaguDagParamsModel) -> str:
        root = self.root.root
        if isinstance(root, DaguDagStepRunCommandModel):
            return DaguDagStepRunCommandModelBuilder(root).to_command(params)
        else:
            return root
