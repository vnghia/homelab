from __future__ import annotations

from pathlib import PosixPath

from homelab_backup.config import BackupHostConfig
from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.volume import ContainerVolumeConfig
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    YamlDumper,
)
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import AbsolutePath, RelativePath
from pulumi import ResourceOptions

from .config import LitestreamConfig


class LitestreamConfigResource(
    ConfigFileResource[JsonDefaultModel], module="litestream", name="Config"
):
    validator = JsonDefaultModel
    dumper = YamlDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        litestream_service: LitestreamService,
    ) -> None:
        config = litestream_service.config
        path = GlobalExtractor(config.path)
        extractor_args = litestream_service.extractor_args
        self.path = path.extract_path(extractor_args)

        dbs = []
        for volume_name, (
            sqlite_backup_volume_resource,
            sqlite_backup_model,
        ) in extractor_args.host.docker.volume.sqlite_backup_volumes.items():
            service = sqlite_backup_volume_resource.service
            data_path = litestream_service.LITESTREAM_DATA_PATH / service / volume_name
            backup_path = (
                litestream_service.LITESTREAM_BACKUP_PATH / service / volume_name
            )

            litestream_service.options[None].add_volumes(
                {
                    volume_name: ContainerVolumeConfig(
                        GlobalExtract.from_simple(data_path.as_posix())
                    ),
                    sqlite_backup_volume_resource.name: ContainerVolumeConfig(
                        GlobalExtract.from_simple(backup_path.as_posix())
                    ),
                }
            )

            for db in sqlite_backup_model.dbs:
                if isinstance(db, str):
                    db_path = RelativePath(PosixPath(db))
                else:
                    db_volume_path = GlobalExtractor(
                        db.with_service(service, False)
                    ).extract_volume_path(extractor_args)
                    if db_volume_path.volume != volume_name:
                        raise ValueError(
                            "Sqlite volume ({}) must be the same as current volume ({})".format(
                                db_volume_path.volume, volume_name
                            )
                        )
                    db_path = db_volume_path.path

                dbs.append(
                    {
                        "path": (data_path / db_path).as_posix(),
                        "replica": {"path": (backup_path / db_path).as_posix()},
                    }
                )

        super().__init__(
            resource_name,
            opts=opts,
            volume_path=path.extract_volume_path(extractor_args),
            data=GlobalExtractor.extract_recursively(config.global_, extractor_args)
            | {"dbs": dbs},
            permission=litestream_service.user,
            extractor_args=extractor_args,
        )


class LitestreamService(ServiceWithConfigResourceBase[LitestreamConfig]):
    LITESTREAM_DATA_PATH = AbsolutePath(PosixPath("/mnt/data"))
    LITESTREAM_BACKUP_PATH = AbsolutePath(PosixPath("/mnt/backup"))

    def __init__(
        self,
        model: ServiceWithConfigModel[LitestreamConfig],
        *,
        opts: ResourceOptions,
        backup_host_config: BackupHostConfig,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.config_file = LitestreamConfigResource(
            "config", opts=self.child_opts, litestream_service=self
        )
        self.options[None].files = [self.config_file]
        self.build_containers()

        self.register_outputs({})
