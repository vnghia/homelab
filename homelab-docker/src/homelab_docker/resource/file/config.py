import dataclasses
import json
from typing import Any

import tomlkit
from pulumi import Input, Output, ResourceOptions

from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.resource.volume import VolumeResource

from . import FileResource
from .schema import Schema


@dataclasses.dataclass
class ConfigFile:
    container_volume_path: ContainerVolumePath
    data: Input[Any]
    schema_url: str | None = None
    schema_override: Any | None = None

    def __post_init__(self) -> None:
        self.schema = (
            Schema(self.schema_url, self.schema_override) if self.schema_url else None
        )

    def toml_dumps(self, raw_data: str) -> str:
        data = json.loads(raw_data)
        if self.schema:
            self.schema.validate(data)
        return tomlkit.dumps(data, sort_keys=True)

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        volume_resource: VolumeResource,
    ) -> FileResource:
        extension = self.container_volume_path.path.suffix
        match extension:
            case ".toml":
                content = Output.json_dumps(self.data).apply(self.toml_dumps)
            case _:
                raise ValueError("Only `toml` format is supported")
        return FileResource(
            resource_name,
            opts=opts,
            container_volume_resource_path=self.container_volume_path.to_resource(
                volume_resource
            ),
            content=content,
        )
