from __future__ import annotations

import typing
from typing import Any

from homelab_dagu_config.model.params import DaguDagParamsModel
from homelab_dagu_config.model.step import DaguDagStepModel
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import Input

from .run import DaguDagStepRunModelBuilder
from .script import DaguDagStepScriptModelBuilder

if typing.TYPE_CHECKING:
    from ... import DaguService


class DaguDagStepModelBuilder(HomelabRootModel[DaguDagStepModel]):
    def to_step(
        self,
        params: DaguDagParamsModel,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        root = self.root

        return (
            {
                "name": root.name,
                "dir": root.dir,
                "executor": root.executor.to_executor(main_service, dotenvs)
                if root.executor
                else None,
                "script": DaguDagStepScriptModelBuilder(root.script).to_script(
                    params, dagu_service, main_service
                )
                if root.script
                else None,
                "output": root.output if root.output else None,
                "depends": root.depends if root.depends else None,
                "preconditions": [
                    precondition.to_step() for precondition in root.preconditions
                ]
                if root.preconditions
                else None,
            }
            | (root.continue_on.to_step() if root.continue_on else {})
            | DaguDagStepRunModelBuilder(root.run).to_run(
                dagu_service, main_service, params
            )
        )
