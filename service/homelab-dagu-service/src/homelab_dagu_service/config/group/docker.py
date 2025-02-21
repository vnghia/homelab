from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel

from homelab_dagu_service.model.step.command import DaguDagStepCommandModel

from ...model import DaguDagModel
from ...model.group.docker import DaguDagDockerGroupModel
from ...model.step.executor.docker import DaguDagStepDockerExecutorModel
from ...model.step.executor.docker.exec import DaguDagStepDockerExecExecutorModel
from ...model.step.executor.docker.run import DaguDagStepDockerRunExecutorModel


class DaguDagDockerRunGroupConfig(HomelabBaseModel):
    run: DaguDagStepDockerRunExecutorModel
    debug: bool = True

    @property
    def model(self) -> DaguDagStepDockerRunExecutorModel:
        return self.run


class DaguDagDockerExecGroupConfig(HomelabBaseModel):
    exec: DaguDagStepDockerExecExecutorModel
    prefix: list[DaguDagStepCommandModel] = []

    @property
    def model(self) -> DaguDagStepDockerExecExecutorModel:
        return self.exec


class DaguDagDockerGroupConfig(HomelabBaseModel):
    executor: DaguDagDockerRunGroupConfig | DaguDagDockerExecGroupConfig
    dags: dict[str, DaguDagDockerGroupModel]
    tags: list[str] = []

    def build_models[T](
        self, main_service: ServiceResourceBase[T]
    ) -> dict[str, DaguDagModel]:
        return {
            name: model.build_model(
                name, DaguDagStepDockerExecutorModel(self.executor.model), main_service
            )
            for name, model in self.dags.items()
        }
