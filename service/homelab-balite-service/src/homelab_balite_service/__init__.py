from homelab_backup.config import BackupGlobalConfig
from homelab_backup.config.volume import BackupVolumeConfig
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.extract.service import ServiceExtractor
from homelab_docker.model.container.volume import ContainerVolumeConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import BaliteConfig


class BaliteService(ServiceWithConfigResourceBase[BaliteConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[BaliteConfig],
        *,
        opts: ResourceOptions,
        backup_config: BackupGlobalConfig,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.source_dir = ServiceExtractor(self.config.source_dir).extract_path(
            self.extractor_args
        )
        self.service_maps: dict[str, list[str]] = {}
        self.volume_configs = {}

        for (
            name,
            volume_model,
        ) in self.docker_resource_args.config.volumes.local.items():
            if (
                isinstance(volume_model.backup, BackupVolumeConfig)
                and len(volume_model.backup.sqlites) > 0
            ):
                service = volume_model.get_service(name)

                self.service_maps[name] = []
                self.volume_configs[name] = ContainerVolumeConfig(
                    GlobalExtract.from_simple(self.get_source_path(name).as_posix())
                )

                for sqlite in volume_model.backup.sqlites:
                    volume_path = GlobalExtractor(sqlite).extract_volume_path(
                        self.SERVICES[service].extractor_args
                    )
                    if volume_path.volume != name:
                        raise ValueError(
                            "Got different name for volume ({} vs {})".format(
                                volume_path.volume, name
                            )
                        )
                    self.service_maps[name].append(volume_path.path.as_posix())

        self.options[None].envs = {
            "HOMELAB_{}_SQLITE".format(name.upper().replace("-", "_")): ",".join(paths)
            for name, paths in self.service_maps.items()
        }
        self.options[None].volumes = self.volume_configs

        self.register_outputs({})

    def get_source_path(self, name: str) -> AbsolutePath:
        return self.source_dir / "{}-sqlite".format(name)
