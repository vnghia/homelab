from __future__ import annotations

import typing

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel

from .. import DaguDagModel
from ..step.executor import DaguDagStepExecutorModel
from ..step.executor.docker import DaguDagStepDockerExecutorModel
from ..step.run import DaguDagStepRunModel
from ..step.run.command import DaguDagStepRunCommandModel

if typing.TYPE_CHECKING:
    from ...config.step.run.command import DaguDagStepRunCommandsConfig


class DaguDagDockerGroupModel(HomelabBaseModel):
    dag: DaguDagModel = DaguDagModel()
    command: DaguDagStepRunCommandModel

    def build_model[T](
        self,
        name: str,
        *,
        main_service: ServiceResourceBase[T],
        docker_executor: DaguDagStepDockerExecutorModel,
        command_config: DaguDagStepRunCommandsConfig,
    ) -> DaguDagModel:
        from ..step import DaguDagStepModel

        return self.dag.__replace__(
            name=name,
            path="{}-{}".format(main_service.name(), name),
            group=main_service.name(),
            steps=[
                DaguDagStepModel(
                    name=name,
                    run=DaguDagStepRunModel(
                        command_config.prefix + self.command + command_config.suffix
                    ),
                    executor=DaguDagStepExecutorModel(docker_executor),
                )
            ],
        )
