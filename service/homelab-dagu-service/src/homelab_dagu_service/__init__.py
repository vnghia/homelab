from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_traefik_service import TraefikService
from homelab_traefik_service.config.dynamic.http import TraefikHttpDynamicConfig
from homelab_traefik_service.config.dynamic.service import TraefikDynamicServiceConfig
from pulumi import ResourceOptions

from .config.group.docker import DaguDagDockerGroupConfig, DaguDagDockerRunGroupConfig
from .model import DaguDagModel
from .model.params import DaguDagParamsModel, DaguDagParamType
from .model.step import DaguDagStepModel
from .model.step.command import (
    DaguDagStepCommandModel,
    DaguDagStepCommandParamModel,
    DaguDagStepCommandParamTypeModel,
)
from .model.step.executor import DaguDagStepExecutorModel
from .model.step.executor.docker import DaguDagStepDockerExecutorModel
from .model.step.executor.docker.run import DaguDagStepDockerRunExecutorModel
from .resource import DaguDagResource


class DaguService(ServiceResourceBase[None]):
    DAGS_DIR_ENV = "DAGU_DAGS_DIR"
    LOG_DIR_ENV = "DAGU_LOG_DIR"

    DEBUG_DAG_NAME = "debug"

    def __init__(
        self,
        model: ServiceModel[None],
        *,
        opts: ResourceOptions | None,
        traefik_service: TraefikService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.dags_directory_container_volume_path = self.model.container.envs[
            self.DAGS_DIR_ENV
        ].as_container_volume_path()
        self.log_directory_container_volume_path = self.model.container.envs[
            self.LOG_DIR_ENV
        ].as_container_volume_path()

        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    envs={"DAGU_TZ": str(self.docker_resource_args.timezone)}
                )
            }
        )

        self.traefik = TraefikHttpDynamicConfig(
            name=self.name(),
            public=False,
            service=TraefikDynamicServiceConfig(
                int(self.model.container.envs["DAGU_PORT"].to_str())
            ),
        ).build_resource(None, opts=self.child_opts, traefik_service=traefik_service)

        self.register_outputs({})

    def get_dag_container_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dags_directory_container_volume_path / name

    def get_dotenv_container_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dags_directory_container_volume_path / name

    def get_log_directory_container_volume_path(self, name: str) -> ContainerVolumePath:
        return self.log_directory_container_volume_path / name

    def build_debug_dag[T](
        self,
        docker_run_executor: DaguDagStepDockerRunExecutorModel,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase[T],
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
                    command=[
                        DaguDagStepCommandModel("sleep"),
                        DaguDagStepCommandModel(
                            DaguDagStepCommandParamModel(
                                param=DaguDagStepCommandParamTypeModel(
                                    type=DaguDagParamType.DEBUG
                                )
                            )
                        ),
                    ],
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

    def build_docker_group_dags[T](
        self,
        docker_group_config: DaguDagDockerGroupConfig,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase[T],
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

        return {
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
