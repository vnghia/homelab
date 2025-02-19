from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from pulumi import ResourceOptions

from . import schema

if typing.TYPE_CHECKING:
    from ... import ResticService


class ResticGlobalProfileResource(
    ConfigFileResource[schema.ResticProfileModel], module="restic", name="Profile"
):
    validator = schema.ResticProfileModel
    dumper = YamlDumper

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        hostname: str,
        restic_service: ResticService,
    ):
        restic_service_model = restic_service.model.container

        super().__init__(
            resource_name,
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
                "profiles": {
                    "base": {
                        "cache-dir": restic_service_model.envs[
                            restic_service.RESTIC_CACHE_ENV
                        ]
                        .as_container_volume_path()
                        .to_container_path(restic_service_model.volumes),
                        "cleanup-cache": True,
                        "backup": {
                            "check-after": True,
                            "source-relative": True,
                            "host": hostname,
                        },
                    }
                },
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
