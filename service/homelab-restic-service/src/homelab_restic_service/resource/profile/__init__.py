from __future__ import annotations

import typing

from homelab_docker.extract import GlobalExtractor
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
    dumper = YamlDumper

    DOCKER_TAG = "docker"

    def __init__(
        self,
        model: ResticProfileModel,
        *,
        opts: ResourceOptions | None,
        restic_service: ResticService,
    ):
        self.volume = model.volume
        self.backup_config = self.volume.model.backup
        if not self.backup_config:
            raise ValueError("`False` backup config should be skipped sooner")

        source = None
        if self.backup_config.source:
            volume_source = GlobalExtractor(
                self.backup_config.source
            ).extract_volume_path(restic_service.SERVICES[self.volume.service], None)
            if volume_source.volume != self.volume.name:
                raise ValueError(
                    "Got different name for volume ({} vs {})".format(
                        volume_source.volume, self.volume.name
                    )
                )
            source = volume_source.path

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
                        | {
                            "tag": ",".join(
                                [self.DOCKER_TAG, self.volume.service] + model.tags
                            ),
                        },
                    }
                },
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
