import configparser
import io
from typing import Any, Generic, TypeVar

import tomlkit
import yaml
from pulumi import Output, ResourceOptions
from pydantic import BaseModel, RootModel, TypeAdapter

from homelab_docker.model.file.config import ConfigFileModel
from homelab_docker.resource.volume import VolumeResource

from . import FileResource

T = TypeVar("T", bound=BaseModel)


class JsonDefaultModel(RootModel[dict[str, Any]]):
    root: dict[str, Any]


class ConfigFileResource(Generic[T], FileResource):
    validator: type[T]

    def __init__(
        self,
        model: ConfigFileModel,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        volume_resource: VolumeResource,
    ):
        self.model = model
        self.data = self.model.data

        extension = self.model.container_volume_path.path.suffix
        match extension:
            case ".toml":
                content = Output.json_dumps(self.data).apply(self.toml_dumps)
            case ".conf":
                content = Output.json_dumps(self.data).apply(self.conf_dumps)
            case ".yaml":
                content = Output.json_dumps(self.data).apply(self.yaml_dumps)
            case _:
                raise ValueError("Only `toml`, `conf`, `yaml` formats are supported")

        super().__init__(
            resource_name,
            opts=opts,
            container_volume_resource_path=self.model.container_volume_path.to_resource(
                volume_resource
            ),
            content=content,
        )

    def validate(self, raw_data: str) -> T:
        return self.validator.model_validate_json(raw_data)

    def toml_dumps(self, raw_data: str) -> str:
        return tomlkit.dumps(
            self.validate(raw_data).model_dump(
                mode="json", by_alias=True, exclude_unset=True, exclude_none=True
            ),
            sort_keys=True,
        )

    def conf_dumps(self, raw_data: str) -> str:
        parser = configparser.ConfigParser()
        for name, section in self.validate(raw_data).model_dump(by_alias=True).items():
            parser.add_section(name)
            for option, value in (
                TypeAdapter(dict[str, str]).validate_python(section).items()
            ):
                parser.set(name, option, value)
        config_content = io.StringIO()
        parser.write(config_content)
        config_content.seek(0)

        content = config_content.read()
        return content

    def yaml_dumps(self, raw_data: str) -> str:
        return yaml.dump(
            self.validate(raw_data).model_dump(
                mode="json", by_alias=True, exclude_unset=True, exclude_none=True
            ),
            default_flow_style=False,
            sort_keys=True,
        )
