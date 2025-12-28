import json
from collections import defaultdict
from pathlib import PosixPath

from homelab_backup.config import BackupHostConfig
from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.docker.container.volume import ContainerVolumeConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath
from pulumi import ResourceOptions

from .config import BaliteConfig


class BaliteService(ServiceWithConfigResourceBase[BaliteConfig]):
    BALITE_DATA_PATH = AbsolutePath(PosixPath("/mnt/data"))
    BALITE_BACKUP_PATH = AbsolutePath(PosixPath("/mnt/backup"))

    def __init__(
        self,
        model: ServiceWithConfigModel[BaliteConfig],
        *,
        opts: ResourceOptions,
        backup_host_config: BackupHostConfig,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        groups: defaultdict[str, list[str]] = defaultdict(list)
        group_all: set[str] = set()
        profiles = {}

        for (
            volume_name,
            sqlite_backup_args,
        ) in extractor_args.host.docker.volume.sqlite_backup_volumes.items():
            service = sqlite_backup_args.volume.service
            data_path = self.BALITE_DATA_PATH / volume_name
            backup_path = self.BALITE_BACKUP_PATH / volume_name

            self.options[None].add_volumes(
                {
                    volume_name: ContainerVolumeConfig(
                        GlobalExtract.from_simple(data_path.as_posix())
                    ),
                    sqlite_backup_args.volume.name: ContainerVolumeConfig(
                        GlobalExtract.from_simple(backup_path.as_posix())
                    ),
                }
            )

            groups[service].append(volume_name)
            group_all.add(service)
            profiles[volume_name] = sqlite_backup_args.dbs

        groups[backup_host_config.BACKUP_KEY_VALUE] = sorted(group_all)

        self.options[None].add_envs(
            {
                "BALITE_SOURCE_DIR": self.BALITE_DATA_PATH.as_posix(),
                "BALITE_DESTINATION_DIR": self.BALITE_BACKUP_PATH.as_posix(),
                "BALITE_GROUPS": json.dumps(groups),
                "BALITE_PROFILES": json.dumps(profiles),
            }
        )

        self.register_outputs({})
