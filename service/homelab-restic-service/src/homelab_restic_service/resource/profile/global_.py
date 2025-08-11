from __future__ import annotations

import functools
import operator
import typing

from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from pulumi import ResourceOptions

from . import schema

if typing.TYPE_CHECKING:
    from ... import ResticService


class ResticGlobalProfileResource(
    ConfigFileResource[schema.ResticProfileModel], module="restic", name="Profile"
):
    validator = schema.ResticProfileModel
    dumper = YamlDumper[schema.ResticProfileModel]

    def __init__(self, *, opts: ResourceOptions, restic_service: ResticService) -> None:
        restic_config = restic_service.config

        all_profiles = restic_service.profiles + restic_service.database_profiles

        group_by_options = {"group-by": "tags,path"}
        snapshot_options = {"path": True, "tag": True}
        forget_options = (
            group_by_options
            | snapshot_options
            | {
                "keep-{}".format(timeframe): number
                for timeframe, number in restic_service.config.keep.last.items()
            }
        )

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
                "includes": [
                    profile.to_path(restic_service.extractor_args)
                    for profile in all_profiles
                ],
                "profiles": {
                    restic_service.DEFAULT_PROFILE_NAME: {
                        "cache-dir": GlobalExtractor(
                            restic_config.cache_dir
                        ).extract_path(restic_service.extractor_args),
                        "cleanup-cache": True,
                        "backup": {
                            "source-relative": True,
                            "host": GlobalExtractor(restic_config.hostname).extract_str(
                                restic_service.extractor_args
                            ),
                            "source": ["."],
                        }
                        | group_by_options,
                        "snapshots": group_by_options | snapshot_options,
                        "forget": forget_options,
                        "ls": {"human-readable": True, "long": True} | snapshot_options,
                        "restore": {"verify": True} | snapshot_options,
                    }
                },
                "groups": {
                    "all": {
                        "profiles": [profile.volume.name for profile in all_profiles]
                    }
                }
                | {
                    service: {"profiles": profiles}
                    for service, profiles in restic_service.service_groups.items()
                }
                | {
                    restic_service.get_database_group(service): {
                        "profiles": functools.reduce(
                            operator.iadd, profiles.values(), []
                        )
                    }
                    for service, profiles in restic_service.service_database_groups.items()
                },
            },
            extractor_args=restic_service.extractor_args,
        )
