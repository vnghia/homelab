from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import (
    ServiceResourceBase,
    ServiceWithConfigResourceBase,
)
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions

from .config import DaguConfig
from .config.group.docker import DaguDagDockerGroupConfig, DaguDagDockerRunGroupConfig
from .model import DaguDagModel
from .model.params import DaguDagParamsModel, DaguDagParamType
from .model.step import DaguDagStepModel
from .model.step.executor import DaguDagStepExecutorModel
from .model.step.executor.docker import DaguDagStepDockerExecutorModel
from .model.step.executor.docker.run import DaguDagStepDockerRunExecutorModel
from .model.step.run import DaguDagStepRunModel
from .model.step.run.command import (
    DaguDagStepRunCommandModel,
    DaguDagStepRunCommandParamModel,
    DaguDagStepRunCommandParamTypeModel,
)
from .resource import DaguDagResource


class DaguService(ServiceWithConfigResourceBase[DaguConfig]):
    DEBUG_DAG_NAME = "debug"

    DAGS: dict[str, dict[str, DaguDagResource]] = {}

    def __init__(
        self,
        model: ServiceWithConfigModel[DaguConfig],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.dags_dir_volume_path = self.config.dags_dir.extract_volume_path(self)
        self.log_dir_volume_path = self.config.log_dir.extract_volume_path(self)

        self.build_containers(options={})

        self.register_outputs({})

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
        container_model_build_args: ContainerModelBuildArgs | None,
        dotenvs: list[DotenvFileResource] | None,
    ) -> DaguDagResource:
        return DaguDagModel(
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
        ).build_resource(
            self.DEBUG_DAG_NAME,
            opts=opts,
            main_service=main_service,
            dagu_service=self,
            container_model_build_args=container_model_build_args,
            dotenvs=dotenvs,
        )

    def build_docker_group_dags(
        self,
        docker_group_config: DaguDagDockerGroupConfig,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        container_model_build_args: ContainerModelBuildArgs | None,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, DaguDagResource]:
        executor_config = docker_group_config.executor
        if isinstance(executor_config, DaguDagDockerRunGroupConfig):
            docker_executor = executor_config.run
            if executor_config.debug:
                self.build_debug_dag(
                    docker_executor,
                    opts=opts,
                    main_service=main_service,
                    container_model_build_args=container_model_build_args,
                    dotenvs=dotenvs,
                )

        if main_service.name() not in self.DAGS:
            self.DAGS[main_service.name()] = {}

        self.DAGS[main_service.name()] |= {
            name: model.build_resource(
                name,
                opts=opts,
                main_service=main_service,
                dagu_service=self,
                container_model_build_args=container_model_build_args,
                dotenvs=dotenvs,
            )
            for name, model in docker_group_config.build_models(
                main_service=main_service
            ).items()
        }

        return self.DAGS[main_service.name()]
