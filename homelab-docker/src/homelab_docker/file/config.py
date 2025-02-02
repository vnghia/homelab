import dataclasses
import json
from typing import Any

import tomlkit
from pulumi import Input, Output, ResourceOptions

from homelab_docker.file import File
from homelab_docker.file.schema import Schema
from homelab_docker.resource import Resource
from homelab_docker.volume_path import VolumePath


@dataclasses.dataclass
class ConfigFile:
    volume_path: VolumePath
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
        resource: Resource,
        opts: ResourceOptions | None = None,
    ) -> File:
        extension = self.volume_path.path.suffix
        match extension:
            case ".toml":
                content = Output.json_dumps(self.data).apply(self.toml_dumps)
            case _:
                raise ValueError("Only `toml` format is supported")
        return File(
            resource_name,
            volume_path=self.volume_path.to_input(resource),
            content=content,
            opts=opts,
        )
