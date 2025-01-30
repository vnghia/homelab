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

    @classmethod
    def toml_dumps(cls, raw_data: str, schema_url: str | None) -> str:
        data = json.loads(raw_data)
        if schema_url:
            Schema(schema_url).validate(data)
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
                content = Output.json_dumps(self.data).apply(
                    lambda x: self.toml_dumps(x, self.schema_url)
                )
            case _:
                raise ValueError("Only `toml` format is supported")
        return File(
            resource_name,
            volume_path=self.volume_path.to_input(resource),
            content=content,
            opts=opts,
        )
