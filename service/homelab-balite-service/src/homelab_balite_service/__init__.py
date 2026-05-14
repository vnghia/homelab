from collections import defaultdict
from pathlib import PosixPath

import orjson
from homelab_backup.config import BackupHostConfig
from homelab_docker.extract import ExtractorArgs
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_pydantic import AbsolutePath, HomelabBaseModel, RelativePath
from pulumi import ResourceOptions

from .config import BaliteConfig
from .hatchet.workflow.balite import HatchetBaliteModelConfig


class BaliteProfileModel(HomelabBaseModel):
    source_volume: str
    source_path: AbsolutePath
    destination_volume: str
    destination_path: AbsolutePath
    paths: list[RelativePath]


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
        profiles: dict[str, BaliteProfileModel] = {}

        for (
            volume_name,
            sqlite_backup_args,
        ) in extractor_args.host.docker.volume.sqlite_backup_volumes.items():
            service = sqlite_backup_args.volume.service
            groups[service].append(volume_name)
            group_all.add(service)
            profiles[volume_name] = BaliteProfileModel(
                source_volume=volume_name,
                source_path=self.BALITE_DATA_PATH / volume_name,
                destination_volume=sqlite_backup_args.volume.name,
                destination_path=self.BALITE_BACKUP_PATH / volume_name,
                paths=sqlite_backup_args.dbs,
            )

        groups[backup_host_config.BACKUP_KEY_VALUE] = sorted(group_all)

        self.options[None].add_envs(
            {
                "BALITE_SOURCE_DIR": self.BALITE_DATA_PATH.as_posix(),
                "BALITE_DESTINATION_DIR": self.BALITE_BACKUP_PATH.as_posix(),
                "BALITE_GROUPS": orjson.dumps(groups).decode(),
                "BALITE_PROFILES": orjson.dumps(
                    {
                        name: [path.as_posix() for path in profile.paths]
                        for name, profile in profiles.items()
                    }
                ).decode(),
            }
        )

        self.config.hatchet.config.root = {
            HatchetBaliteModelConfig.CONFIG_KEY: {
                "container": None,
                "balite": {
                    "groups": groups,
                    "profiles": {
                        name: {
                            "source_volume": self.extractor_args.host.docker.volume.volumes[
                                profile.source_volume
                            ].resource.name,
                            "source_path": profile.source_path,
                            "destination_volume": self.extractor_args.host.docker.volume.volumes[
                                profile.destination_volume
                            ].resource.name,
                            "destination_path": profile.destination_path,
                        }
                        for name, profile in profiles.items()
                    },
                },
            }
        }

        self.build_containers()

        self.register_outputs({})
