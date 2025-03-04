from __future__ import annotations

import typing
from typing import Any

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.command import DaguDagStepRunCommandModel
from homelab_pydantic import HomelabRootModel

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunCommandModelBuilder(HomelabRootModel[DaguDagStepRunCommandModel]):
    def to_run(
        self,
        dagu_service_: DaguService,
        params: DaguDagParamsModel,
    ) -> dict[str, Any]:
        return {
            "command": " ".join(
                self.root.command_to_str(command, params) for command in self.root.root
            )
        }
