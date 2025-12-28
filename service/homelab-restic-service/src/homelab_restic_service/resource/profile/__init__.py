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

        source = (
            GlobalExtractor.extract_relative_path(
                self.backup_config.source,
                self.volume.service,
                self.main_service.extractor_args,
                self.volume.name,
            )
            if self.backup_config.source
            else None
        )
        target = (
            (
                self.volume.path
                / (source if not self.backup_config.file else source.parent)
            )
            if source
            else self.volume.path
        )

        exclude = self.backup_config.excludes

        super().__init__(
            self.volume.name,
            opts=opts,
            volume_path=restic_service.get_profile_volume_path(self.volume.name),
            data={
                "version": "2",
                "profiles": {
                    self.volume.name: {
                        "base-dir": self.volume.path,
                        "inherit": restic_service.get_repository_profile_name(
                            model.volume.repository
                        ),
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
            permission=restic_service.user,
            extractor_args=restic_service.extractor_args,
        )
