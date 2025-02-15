from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.database.postgres import PostgresDatabaseModel
from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.model.service import ServiceModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.file.config import ConfigFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from .config import BarmanConfig


class BarmanService(ServiceResourceBase[BarmanConfig]):
    def __init__(
        self,
        model: ServiceModel[BarmanConfig],
        *,
        opts: ResourceOptions | None,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.configs: list[ConfigFileResource] = []
        for (
            service_name,
            source_config,
        ) in self.args.database_source_configs.items():
            for name, sources in source_config.postgres.items():
                for version, source in sources.items():
                    full_name = PostgresDatabaseModel.get_full_name_version(
                        service_name, name, version
                    )
                    file = ConfigFileModel(
                        container_volume_path=self.config.get_config_container_volume_path(
                            full_name
                        ),
                        data={
                            full_name: {
                                "description": full_name,
                                "conninfo": source.to_kv({"sslmode": "disable"}),
                                "backup_method": "postgres",
                                "archiver": "off",
                                "streaming_archiver": "on",
                                "slot_name": self.name(),
                                "create_slot": "auto",
                                "minimum_redundancy": str(
                                    self.config.minimum_redundancy
                                ),
                                "retention_policy": self.config.retention_policy,
                                "local_staging_path": self.config.staging_dir.to_container_path(
                                    self.model.container.volumes
                                ).as_posix(),
                            }
                        },
                    ).build_resource(
                        full_name,
                        opts=self.child_opts,
                        volume_resource=self.docker_resource_args.volume,
                    )
                    self.configs.append(file)

        self.build_containers(
            options={None: ContainerModelBuildArgs(files=self.configs)}
        )

        self.register_outputs({})
