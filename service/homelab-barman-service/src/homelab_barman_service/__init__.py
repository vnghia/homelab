from homelab_backup.config import BackupConfig
from homelab_dagu_service import DaguService
from homelab_dagu_service.model import DaguDagModel
from homelab_dagu_service.model.params import DaguDagParamsModel
from homelab_dagu_service.model.step import DaguDagStepModel
from homelab_dagu_service.model.step.command import (
    DaguDagStepCommandModel,
    DaguDagStepCommandParamModel,
)
from homelab_dagu_service.model.step.executor import DaguDagStepExecutorModel
from homelab_dagu_service.model.step.executor.docker import (
    DaguDagStepDockerExecutorModel,
)
from homelab_dagu_service.model.step.executor.docker.exec import (
    DaguDagStepDockerExecExecutorModel,
)
from homelab_dagu_service.resource import DaguDagResource
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from .config import BarmanConfig
from .resource import BarmanConfigFileResource


class BarmanService(ServiceResourceBase[BarmanConfig]):
    def __init__(
        self,
        model: ServiceModel[BarmanConfig],
        *,
        opts: ResourceOptions | None,
        backup_config: BackupConfig,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.backup_config = backup_config

        self.configs: list[BarmanConfigFileResource] = []
        for (
            service_name,
            source_config,
        ) in self.args.database_source_configs.items():
            for name, sources in source_config.postgres.items():
                for version, source in sources.items():
                    full_name = PostgresDatabaseModel.get_full_name_version(
                        service_name, name, version
                    )
                    self.configs.append(
                        BarmanConfigFileResource(
                            resource_name=full_name,
                            opts=self.child_opts,
                            database_source_model=source,
                            barman_service=self,
                        )
                    )

        self.build_containers(
            options={None: ContainerModelBuildArgs(files=self.configs)}
        )

        self.executor = DaguDagStepExecutorModel(
            DaguDagStepDockerExecutorModel(
                DaguDagStepDockerExecExecutorModel(container=None)
            )
        )

        self.dagu_dags: dict[str, DaguDagResource] = {}
        for name, task in self.config.dagu.tasks.items():
            self.dagu_dags[name] = DaguDagModel(
                name=name,
                path="{}-{}".format(self.name(), name),
                group=self.name(),
                tags=self.config.dagu.tags,
                schedule=task.schedule,
                max_active_runs=1,
                params=DaguDagParamsModel(
                    {
                        self.backup_config.BACKUP_PROFILE_KEY: self.backup_config.BACKUP_PROFILE_VALUE
                    }
                ),
                steps=[
                    DaguDagStepModel(
                        name=name,
                        command=[DaguDagStepCommandModel("barman")]
                        + [DaguDagStepCommandModel(command) for command in task.command]
                        + [
                            DaguDagStepCommandModel(
                                DaguDagStepCommandParamModel(
                                    param=self.backup_config.BACKUP_PROFILE_KEY
                                )
                            )
                        ],
                        executor=self.executor,
                    )
                ],
            ).build_resource(
                name,
                opts=self.child_opts,
                main_service=self,
                dagu_service=dagu_service,
                container_model_build_args=None,
                dotenvs=None,
            )

        self.register_outputs({})
