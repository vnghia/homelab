import dataclasses
import typing
from typing import Any, Mapping

from pulumi import Input, ResourceOptions
from pydantic import HttpUrl

from ..container.volume_path import ContainerVolumePath

if typing.TYPE_CHECKING:
    from ...resource.file.config import ConfigFileResource
    from ...resource.volume import VolumeResource


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
        volume_resource: "VolumeResource",
    ) -> "ConfigFileResource":
        from ...resource.file.config import ConfigFileResource

        return ConfigFileResource(
            self, resource_name, opts=opts, volume_resource=volume_resource
        )
