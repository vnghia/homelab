from __future__ import annotations

import typing
from typing import Any

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step.run.command import (
    DaguDagStepRunCommandFullModel,
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
)
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from .... import DaguService


class DaguDagStepRunCommandFullModelBuilder(
    HomelabRootModel[DaguDagStepRunCommandFullModel]
):
    def to_command(
        self, params: DaguDagParamsModel, main_service: ServiceResourceBase
    ) -> Output[str]:
        root = self.root.root
        if isinstance(root, DaguDagStepRunCommandParamModel):
            value = params.to_key_command(root.param)
            return Output.from_input(root.transform.transform(value))
        return GlobalExtractor(root).extract_str(main_service, None)


class DaguDagStepRunCommandModelBuilder(HomelabRootModel[DaguDagStepRunCommandModel]):
    def to_command(
        self, params: DaguDagParamsModel, main_service: ServiceResourceBase
    ) -> Output[str]:
        return Output.all(
            *(
                DaguDagStepRunCommandFullModelBuilder(command).to_command(
                    params, main_service
                )
                for command in self.root.root
            )
        ).apply(" ".join)

    def to_run(
        self,
        params: DaguDagParamsModel,
        dagu_service_: DaguService,
        main_service: ServiceResourceBase,
    ) -> dict[str, Any]:
        return {"command": self.to_command(params, main_service)}
