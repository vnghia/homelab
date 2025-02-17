import typing

from homelab_docker.resource.file.config import ConfigFileResource, TomlDumper
from pulumi import ResourceOptions

from ...model import schema

if typing.TYPE_CHECKING:
    from ... import ResticService


class ResticGlobalProfileResource(
    ConfigFileResource[schema.Model], module="restic", name="Profile"
):
    validator = schema.Model
    dumper = TomlDumper

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        restic_service: "ResticService",
    ):
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
            },
            volume_resource=restic_service.docker_resource_args.volume,
        )
