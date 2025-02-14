import configparser
import dataclasses
import io
import json
from typing import Any

import deepmerge
import httpx
import jsonschema
import tomlkit
import yaml
from pulumi import Input, Output, ResourceOptions

from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.resource.file import FileResource
from homelab_docker.resource.volume import VolumeResource


class Schema:
    def __init__(self, url: str, override: Any | None = None) -> None:
        self.schema = deepmerge.always_merger.merge(
            httpx.get(url=url).raise_for_status().json(), override or {}
        )

    def validate(self, data: Any) -> None:
        jsonschema.validate(data, self.schema)


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

    def conf_dumps(self, raw_data: str) -> str:
        data = json.loads(raw_data)
        if self.schema:
            self.schema.validate(data)

        parser = configparser.ConfigParser()
        for remote_name, remote in data.items():
            parser.add_section(remote_name)
            for k, v in remote.items():
                parser.set(remote_name, k, v)
        config_content = io.StringIO()
        parser.write(config_content)
        config_content.seek(0)

        content = config_content.read()
        return content

    def yaml_dumps(self, raw_data: str) -> str:
        data = json.loads(raw_data)
        if self.schema:
            self.schema.validate(data)
        return yaml.dump(data, default_flow_style=False, sort_keys=True)

    def env_dumps(self, raw_data: str) -> str:
        data = json.loads(raw_data)
        if self.schema:
            self.schema.validate(data)
        return (
            "\n".join(
                [
                    '{}="{}"'.format(k, v.replace('"', '\\"'))
                    for k, v in sorted(data.items(), key=lambda x: x[0])
                ]
            )
            + "\n"
        )

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
            case ".conf":
                content = Output.json_dumps(self.data).apply(self.conf_dumps)
            case ".yaml":
                content = Output.json_dumps(self.data).apply(self.yaml_dumps)
            case ".env":
                content = Output.json_dumps(self.data).apply(self.env_dumps)
            case _:
                raise ValueError(
                    "Only `toml`, `conf`, `yaml`, `env` formats are supported"
                )
        return FileResource(
            resource_name,
            opts=opts,
            container_volume_resource_path=self.container_volume_path.to_resource(
                volume_resource
            ),
            content=content,
        )
