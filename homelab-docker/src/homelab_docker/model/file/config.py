import dataclasses
import typing
from typing import Any, Mapping

from pulumi import Input, ResourceOptions
from pydantic import HttpUrl

from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.resource.volume import VolumeResource

if typing.TYPE_CHECKING:
    from homelab_docker.resource.file.config import ConfigFileResource


@dataclasses.dataclass
class ConfigFileModel:
    container_volume_path: ContainerVolumePath
    data: Mapping[str, Input[Any]]
    schema_url: HttpUrl | None = None
    schema_override: dict[str, Any] | None = None

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        volume_resource: VolumeResource,
    ) -> "ConfigFileResource":
        from homelab_docker.resource.file.config import ConfigFileResource

        return ConfigFileResource(
            self, resource_name, opts=opts, volume_resource=volume_resource
        )
