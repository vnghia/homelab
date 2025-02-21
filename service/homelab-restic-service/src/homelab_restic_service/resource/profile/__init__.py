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
        self.name = model.volume
        self.service = self.name.split("-", maxsplit=1)[0]

        super().__init__(
            self.name,
            opts=opts,
            container_volume_path=restic_service.config.get_profile_container_volume_path(
                self.name
            ),
            data={
                "version": "2",
                "profiles": {
                    self.name: {
                        "base-dir": restic_service.get_volume_path(self.name),
                        "inherit": restic_service.DEFAULT_PROFILE_NAME,
                        "backup": {
                            "tag": ",".join([self.DOCKER_TAG, self.service]),
                        },
                    }
                },
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
