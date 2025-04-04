from __future__ import annotations

import typing
from typing import Any

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run import DaguDagStepRunModel
from homelab_dagu_config.model.step.run.command import DaguDagStepRunCommandModel
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel

from .command import DaguDagStepRunCommandModelBuilder
from .subdag import DaguDagStepRunSubdagModelBuilder

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunModelBuilder(HomelabRootModel[DaguDagStepRunModel]):
    def to_run(
        self,
        dagu_service: DaguService,
        main_service: ServiceResourceBase,
        params: DaguDagParamsModel,
    ) -> dict[str, Any]:
        root = self.root.root

        return (
            DaguDagStepRunCommandModelBuilder(root)
            if isinstance(root, DaguDagStepRunCommandModel)
            else DaguDagStepRunSubdagModelBuilder(root)
        ).to_run(params, dagu_service, main_service)
