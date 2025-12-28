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

        group_by_options = {"group-by": "tags,path"}
        snapshot_options = {"path": True, "tag": True}

        all_profiles_path = []
        all_profiles_name = []
        for profile in restic_service.profiles:
            all_profiles_path.append(profile.to_path(restic_service.extractor_args))
            all_profiles_name.append(profile.volume.name)
        for profile in restic_service.database_profiles:
            all_profiles_path.append(profile.to_path(restic_service.extractor_args))
            all_profiles_name.append(profile.volume.name)

        super().__init__(
            "global",
            opts=opts,
            volume_path=restic_service.get_global_profile_volume_path(),
            data={
                "version": "2",
                "global": {
                    "command-output": "console",
                    "initialize": False,
                    "group-continue-on-error": True,
                },
                "includes": all_profiles_path,
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
                        "forget": group_by_options | snapshot_options,
                        "ls": {"human-readable": True, "long": True} | snapshot_options,
                        "restore": {"verify": True} | snapshot_options,
                    }
                }
                | restic_service.repositores,
                "groups": {"all": {"profiles": all_profiles_name}}
                | {
                    service: {"profiles": profiles}
                    for service, profiles in restic_service.service_groups.items()
                }
                | {
                    restic_service.get_database_group(service): {
                        "profiles": functools.reduce(
                            operator.iadd,
                            [
                                [profile.name for profile in profiles]
                                for profiles in service_database_args.values()
                            ],
                            [],
                        )
                    }
                    for service, service_database_args in restic_service.service_database_groups.items()
                },
            },
            permission=restic_service.user,
            extractor_args=restic_service.extractor_args,
        )
