from __future__ import annotations

import typing
from typing import Any

from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import Input

from .continue_on import DaguDagStepContinueOnModel
from .executor import DaguDagStepExecutorModel
from .run import DaguDagStepRunModel

if typing.TYPE_CHECKING:
    from ... import DaguService
    from ..params import DaguDagParamsModel


class DaguDagStepModel(HomelabBaseModel):
    name: str
    run: DaguDagStepRunModel
    continue_on: DaguDagStepContinueOnModel | None = None
    executor: DaguDagStepExecutorModel | None = None

    def to_step(
        self,
        params: DaguDagParamsModel,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return (
            {
                "name": self.name,
                "executor": self.executor.to_executor(main_service, dotenvs)
                if self.executor
                else None,
            }
            | (self.continue_on.to_step() if self.continue_on else {})
            | self.run.to_run(dagu_service, params)
        )
