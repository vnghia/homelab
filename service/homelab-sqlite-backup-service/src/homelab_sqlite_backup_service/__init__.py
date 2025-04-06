from pathlib import PosixPath

from homelab_backup.config import BackupGlobalConfig
from homelab_docker.extract import GlobalExtractor
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import SqliteBackupConfig


class SqliteBackupService(ServiceWithConfigResourceBase[SqliteBackupConfig]):
    SQLITE_BACKUP_MOUNT_PATH: AbsolutePath = AbsolutePath(PosixPath("/mnt"))

    def __init__(
        self,
        model: ServiceWithConfigModel[SqliteBackupConfig],
        *,
        opts: ResourceOptions | None,
        backup_config: BackupGlobalConfig,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.database_configs = {}
        self.volume_configs = {}

        for (
            name,
            volume_model,
        ) in self.docker_resource_args.config.volumes.local.items():
            if volume_model.backup:
                if len(volume_model.backup.sqlites) > 0:
                    service = volume_model.get_service(name)
                    self.volume_configs[name] = ContainerVolumeConfig(
                        GlobalExtract.from_simple(
                            (self.SQLITE_BACKUP_MOUNT_PATH / name).as_posix()
                        )
                    )
                    for sqlite in volume_model.backup.sqlites:
                        volume_path = GlobalExtractor(sqlite).extract_volume_path(
                            self.SERVICES[service], None
                        )
                        if volume_path.volume != name:
                            raise ValueError(
                                "Got different name for volume ({} vs {})".format(
                                    volume_path.volume, name
                                )
                            )

        self.options[None].volumes = self.volume_configs

        self.register_outputs({})
