from __future__ import annotations

import typing
from typing import Any

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pydantic import field_validator

from .. import DaguDagModel
from ..step.command import DaguDagStepCommandModel
from ..step.executor import DaguDagStepExecutorModel
from ..step.executor.docker import DaguDagStepDockerExecutorModel

if typing.TYPE_CHECKING:
    from ...config.step.command import DaguDagStepCommandConfig


class DaguDagDockerGroupModel(HomelabBaseModel):
    dag: DaguDagModel
    command: list[DaguDagStepCommandModel]

    @field_validator("dag", mode="before")
    @classmethod
    def add_default_steps(cls, data: Any) -> Any:
        if isinstance(data, dict):
            data["steps"] = []
        return data

    def build_model[T](
        self,
        name: str,
        *,
        main_service: ServiceResourceBase[T],
        docker_executor: DaguDagStepDockerExecutorModel,
        command_config: DaguDagStepCommandConfig,
    ) -> DaguDagModel:
        from ..step import DaguDagStepModel

        return self.dag.__replace__(
            name=name,
            path="{}-{}".format(main_service.name(), name),
            group=main_service.name(),
            steps=[
                DaguDagStepModel(
                    name=name,
                    command=command_config.prefix
                    + self.command
                    + command_config.suffix,
                    executor=DaguDagStepExecutorModel(docker_executor),
                )
            ],
        )
