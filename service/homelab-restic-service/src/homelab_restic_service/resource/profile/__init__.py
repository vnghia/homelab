from __future__ import annotations

import typing

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from pulumi import ResourceOptions

from ...model.profile import ResticProfileModel
from . import schema

if typing.TYPE_CHECKING:
    from ... import ResticService


class ResticProfileResource(
    ConfigFileResource[schema.ResticProfileModel], module="restic", name="Profile"
):
    validator = schema.ResticProfileModel
    dumper = YamlDumper[schema.ResticProfileModel]

    DOCKER_TAG = "docker"

    def __init__(
        self,
        model: ResticProfileModel,
        *,
        opts: ResourceOptions,
        restic_service: ResticService,
    ) -> None:
        self.volume = model.volume
        self.backup_config = self.volume.model.backup
        if not self.backup_config:
            raise ValueError("`False` backup config should be skipped sooner")

        self.main_service = restic_service.extractor_args.services[self.volume.service]

        source = None
        if self.backup_config.source:
            volume_source = GlobalExtractor(
                self.backup_config.source
            ).extract_volume_path(self.main_service.extractor_args)
            if volume_source.volume != self.volume.name:
                raise ValueError(
                    "Got different name for volume ({} vs {})".format(
                        volume_source.volume, self.volume.name
                    )
                )
            source = volume_source.path
        target = (
            (
                self.volume.path
                / (source if not self.backup_config.file else source.parent)
            )
            if source
            else self.volume.path
        )

        exclude = self.backup_config.excludes
        if len(self.backup_config.sqlites) > 0:
            for path in self.backup_config.sqlites:
                volume_path = GlobalExtractor(path).extract_volume_path(
                    self.main_service.extractor_args
                )
                if volume_path.volume != self.volume.name:
                    raise ValueError(
                        "Got different name for volume ({} vs {})".format(
                            volume_path.volume, self.volume.name
                        )
                    )
                exclude += [
                    volume_path.path,
                    volume_path.path.with_suffix(
                        "{}-shm".format(volume_path.path.suffix)
                    ),
                    volume_path.path.with_suffix(
                        "{}-wal".format(volume_path.path.suffix)
                    ),
                ]

        super().__init__(
            self.volume.name,
            opts=opts,
            volume_path=restic_service.get_profile_volume_path(self.volume.name),
            data={
                "version": "2",
                "profiles": {
                    self.volume.name: {
                        "base-dir": self.volume.path,
                        "inherit": restic_service.DEFAULT_PROFILE_NAME,
                        "backup": ({"source": [source]} if source else {})
                        | ({"exclude": exclude} if exclude else {})
                        | {
                            "tag": ",".join(
                                [self.DOCKER_TAG, self.volume.service, *model.tags]
                            ),
                        },
                        "restore": {"target": target},
                    }
                },
            },
            docker_resource_args=restic_service.docker_resource_args,
        )
