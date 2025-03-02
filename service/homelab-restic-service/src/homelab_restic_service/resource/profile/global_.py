from __future__ import annotations

import itertools
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
        restic_config = restic_service.config
        restic_model = restic_service.model[restic_config.profile_dir.container]

        forget_options = {"prune": True} | {
            "keep-{}".format(timeframe): number
            for timeframe, number in restic_service.config.keep.last.items()
        }
        super().__init__(
            "global",
            opts=opts,
            volume_path=restic_service.get_profile_volume_path("profiles"),
            data={
                "version": "2",
                "global": {
                    "command-output": "console",
                    "initialize": False,
                },
                "includes": [profile.to_path(restic_model) for profile in profiles],
                "profiles": {
                    restic_service.DEFAULT_PROFILE_NAME: {
                        "cache-dir": restic_config.cache_dir.extract_path(
                            restic_service
                        ),
                        "cleanup-cache": True,
                        "backup": {
                            "check-before": True,
                            "check-after": True,
                            "source-relative": True,
                            "host": hostname,
                            "source": ["."],
                        },
                        "forget": forget_options,
                        "retention": {"after-backup": True} | forget_options,
                    }
                },
                "groups": {"all": {"profiles": [profile.name for profile in profiles]}}
                | {
                    service: {"profiles": [profile.name for profile in group]}
                    for service, group in itertools.groupby(
                        profiles, key=lambda x: x.service
                    )
                },
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
