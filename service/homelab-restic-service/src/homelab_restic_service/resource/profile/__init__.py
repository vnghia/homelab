from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from pulumi import ResourceOptions

from ...model import ResticProfileModel
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
                        "backup": {
                            "tag": ",".join(
                                [self.DOCKER_TAG, self.volume.service] + model.tags
                            ),
                        },
                    }
                },
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
