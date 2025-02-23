from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel

from ...model import DaguDagModel
from ...model.group.docker import DaguDagDockerGroupModel
from ...model.step.executor.docker import DaguDagStepDockerExecutorModel
from ...model.step.executor.docker.exec import DaguDagStepDockerExecExecutorModel
from ...model.step.executor.docker.run import DaguDagStepDockerRunExecutorModel
from ..step.run.command import DaguDagStepRunCommandsConfig


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

    dag: DaguDagModel = DaguDagModel()
    command: DaguDagStepRunCommandsConfig = DaguDagStepRunCommandsConfig()

    dags: dict[str, DaguDagDockerGroupModel]

    def build_models(
        self, *, main_service: ServiceResourceBase
    ) -> dict[str, DaguDagModel]:
        global_dag = self.dag
        return {
            name: model.__replace__(dag=global_dag.model_merge(model.dag)).build_model(
                name,
                main_service=main_service,
                docker_executor=DaguDagStepDockerExecutorModel(self.executor.model),
                command_config=self.command,
            )
            for name, model in self.dags.items()
        }
