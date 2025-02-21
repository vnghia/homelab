from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel

from ...model import DaguDagModel
from ...model.group.docker import DaguDagDockerGroupModel
from ...model.step.executor.docker import DaguDagStepDockerExecutorModel
from ...model.step.executor.docker.exec import DaguDagStepDockerExecExecutorModel
from ...model.step.executor.docker.run import DaguDagStepDockerRunExecutorModel
from ..step.command import DaguDagStepCommandConfig


class DaguDagDockerRunGroupConfig(HomelabBaseModel):
    run: DaguDagStepDockerRunExecutorModel
    debug: bool = True

    @property
    def model(self) -> DaguDagStepDockerRunExecutorModel:
        return self.run


class DaguDagDockerExecGroupConfig(HomelabBaseModel):
    exec: DaguDagStepDockerExecExecutorModel

    @property
    def model(self) -> DaguDagStepDockerExecExecutorModel:
        return self.exec


class DaguDagDockerGroupConfig(HomelabBaseModel):
    executor: DaguDagDockerRunGroupConfig | DaguDagDockerExecGroupConfig
    tags: list[str] = []
    command: DaguDagStepCommandConfig = DaguDagStepCommandConfig()
    dags: dict[str, DaguDagDockerGroupModel]

    def build_models[T](
        self, *, main_service: ServiceResourceBase[T]
    ) -> dict[str, DaguDagModel]:
        return {
            name: model.__replace__(
                dag=model.dag.__replace__(tags=self.tags)
            ).build_model(
                name,
                main_service=main_service,
                docker_executor=DaguDagStepDockerExecutorModel(self.executor.model),
                command_config=self.command,
            )
            for name, model in self.dags.items()
        }
