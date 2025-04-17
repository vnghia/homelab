from __future__ import annotations

import typing

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.command import DaguDagStepRunCommandModel
from homelab_dagu_config.model.step.script import DaguDagStepScriptModel
from homelab_docker.extract import GlobalExtractor
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic.model import HomelabRootModel
from pulumi import Output

from homelab_dagu_service.model.step.run.command import (
    DaguDagStepRunCommandModelBuilder,
)

if typing.TYPE_CHECKING:
    from ... import DaguService


class DaguDagStepScriptModelBuilder(HomelabRootModel[DaguDagStepScriptModel]):
    def to_script(
        self,
        params: DaguDagParamsModel,
        dagu_service: DaguService,
        main_service: ServiceResourceBase,
    ) -> Output[str]:
        root = self.root.root
        if isinstance(root, DaguDagStepRunCommandModel):
            return DaguDagStepRunCommandModelBuilder(root).to_command(
                params,
                main_service,
            )
        return GlobalExtractor(root).extract_str(main_service, None)
