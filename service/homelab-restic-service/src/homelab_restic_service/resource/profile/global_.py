from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from pulumi import ResourceOptions

from . import schema

if typing.TYPE_CHECKING:
    from ... import ResticService
    from . import ResticProfileResource


class ResticGlobalProfileResource(
    ConfigFileResource[schema.ResticProfileModel], module="restic", name="Profile"
):
    validator = schema.ResticProfileModel
    dumper = YamlDumper

    def __init__(
        self,
        *,
        opts: ResourceOptions | None,
        hostname: str,
        profiles: list[ResticProfileResource],
        restic_service: ResticService,
    ):
        restic_service_model = restic_service.model.container
        restic_volumes_config = restic_service_model.volumes

        super().__init__(
            "global",
            opts=opts,
            container_volume_path=restic_service.config.get_profile_container_volume_path(
                "profiles"
            ),
            data={
                "version": "2",
                "global": {
                    "command-output": "console",
                    "initialize": False,
                },
                "includes": [
                    profile.to_container_path(restic_volumes_config)
                    for profile in profiles
                ],
                "profiles": {
                    restic_service.BASE_PROFILE_NAME: {
                        "cache-dir": restic_service_model.envs[
                            restic_service.RESTIC_CACHE_ENV
                        ]
                        .as_container_volume_path()
                        .to_container_path(restic_volumes_config),
                        "cleanup-cache": True,
                        "backup": {
                            "check-after": True,
                            "source-relative": True,
                            "host": hostname,
                            "source": ["."],
                        },
                    }
                },
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
