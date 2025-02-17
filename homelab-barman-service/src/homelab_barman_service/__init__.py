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
from homelab_docker.model.database.source import DatabaseSourceModel
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    IniDumper,
    JsonDefaultModel,
)
from homelab_docker.resource.service import ServiceResourceBase
from homelab_docker.resource.volume import VolumeResource
from pulumi import ResourceOptions

from .config import BarmanConfig


class BarmanConfigFileResource(
    ConfigFileResource[JsonDefaultModel], module="barman", name="Config"
):
    validator = JsonDefaultModel
    dumper = IniDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        service_name: str,
        barman_service_model: ServiceModel[BarmanConfig],
        source: DatabaseSourceModel,
        volume_resource: VolumeResource,
    ):
        config = barman_service_model.config
        super().__init__(
            resource_name,
            opts=opts,
            container_volume_path=config.get_config_container_volume_path(
                resource_name
            ),
            data={
                resource_name: {
                    "description": resource_name,
                    "conninfo": source.to_kv({"sslmode": "disable"}),
                    "backup_method": "postgres",
                    "archiver": "off",
                    "streaming_archiver": "on",
                    "slot_name": service_name,
                    "create_slot": "auto",
                    "minimum_redundancy": str(config.minimum_redundancy),
                    "last_backup_maximum_age": config.last_backup_maximum_age,
                    "retention_policy": config.retention_policy,
                    "local_staging_path": config.staging_dir.to_container_path(
                        barman_service_model.container.volumes
                    ).as_posix(),
                }
            },
            volume_resource=volume_resource,
        )


class BarmanService(ServiceResourceBase[BarmanConfig]):
    SERVER_NAME_KEY = "SERVER_NAME"

    def __init__(
        self,
        model: ServiceModel[BarmanConfig],
        *,
        opts: ResourceOptions | None,
        dagu_service: DaguService,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

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
                            service_name=self.name(),
                            barman_service_model=self.model,
                            source=source,
                            volume_resource=self.docker_resource_args.volume,
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
                params=DaguDagParamsModel({self.SERVER_NAME_KEY: "all"}),
                steps=[
                    DaguDagStepModel(
                        name=name,
                        command=[DaguDagStepCommandModel("barman")]
                        + [DaguDagStepCommandModel(command) for command in task.command]
                        + [
                            DaguDagStepCommandModel(
                                DaguDagStepCommandParamModel(param=self.SERVER_NAME_KEY)
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
                build_args=None,
                dotenv=None,
            )

        self.register_outputs({})
