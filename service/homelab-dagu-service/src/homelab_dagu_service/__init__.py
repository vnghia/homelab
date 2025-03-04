from collections import defaultdict

from homelab_dagu_config.group.docker import (
    DaguDagDockerGroupConfig,
    DaguDagDockerRunGroupConfig,
)
from homelab_dagu_config.model import DaguDagModel
from homelab_dagu_config.model.params import DaguDagParamsModel, DaguDagParamType
from homelab_dagu_config.model.step import DaguDagStepModel
from homelab_dagu_config.model.step.executor import DaguDagStepExecutorModel
from homelab_dagu_config.model.step.executor.docker import (
    DaguDagStepDockerExecutorModel,
)
from homelab_dagu_config.model.step.executor.docker.run import (
    DaguDagStepDockerRunExecutorModel,
)
from homelab_dagu_config.model.step.run import DaguDagStepRunModel
from homelab_dagu_config.model.step.run.command import (
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeModel,
)
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extra_service import ExtraService
from pulumi import ResourceOptions

from .config import DaguConfig
from .model import DaguDagModelBuilder
from .resource import DaguDagResource


class DaguService(ExtraService[DaguConfig]):
    DEBUG_DAG_NAME = "debug"

    def __init__(
        self,
        model: ServiceWithConfigModel[DaguConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.dags_dir_volume_path = self.config.dags_dir.extract_volume_path(self, None)
        self.log_dir_volume_path = self.config.log_dir.extract_volume_path(self, None)

        self.dotenvs: defaultdict[str, dict[str | None, DotenvFileResource]] = (
            defaultdict(dict)
        )
        self.dags: defaultdict[str, dict[str, DaguDagResource]] = defaultdict(dict)

    def get_dag_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dags_dir_volume_path / name

    def get_dotenv_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dags_dir_volume_path / name

    def get_log_dir_volume_path(self, name: str) -> ContainerVolumePath:
        return self.log_dir_volume_path / name

    def build_debug_dag(
        self,
        docker_run_executor: DaguDagStepDockerRunExecutorModel,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
    ) -> DaguDagResource:
        return DaguDagModelBuilder(
            DaguDagModel(
                name=self.DEBUG_DAG_NAME,
                path="{}-{}".format(main_service.name(), self.DEBUG_DAG_NAME),
                group=main_service.name(),
                tags=[self.DEBUG_DAG_NAME],
                params=DaguDagParamsModel(types={DaguDagParamType.DEBUG: None}),
                steps=[
                    DaguDagStepModel(
                        name=self.DEBUG_DAG_NAME,
                        run=DaguDagStepRunModel(
                            DaguDagStepRunCommandModel(
                                [
                                    "sleep",
                                    DaguDagStepRunCommandParamModel(
                                        param=DaguDagStepRunCommandParamTypeModel(
                                            type=DaguDagParamType.DEBUG
                                        )
                                    ),
                                ]
                            )
                        ),
                        executor=DaguDagStepExecutorModel(
                            DaguDagStepDockerExecutorModel(
                                docker_run_executor.__replace__(entrypoint=[])
                            )
                        ),
                    )
                ],
            )
        ).build_resource(
            self.DEBUG_DAG_NAME, opts=opts, main_service=main_service, dagu_service=self
        )

    def build_docker_group_dags(
        self,
        docker_group_config: DaguDagDockerGroupConfig,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
    ) -> dict[str, DaguDagResource]:
        executor_config = docker_group_config.executor
        if isinstance(executor_config, DaguDagDockerRunGroupConfig):
            docker_executor = executor_config.run
            if executor_config.debug:
                self.build_debug_dag(
                    docker_executor, opts=opts, main_service=main_service
                )

        self.dags[main_service.name()] |= {
            name: DaguDagModelBuilder(model).build_resource(
                name, opts=opts, main_service=main_service, dagu_service=self
            )
            for name, model in docker_group_config.build_models(
                main_service=main_service
            ).items()
        }

        return self.dags[main_service.name()]
