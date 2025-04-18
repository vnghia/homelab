import abc
import configparser
import io
from typing import Any, ClassVar, Generic, Mapping, TypeVar

import jsonschema
import tomlkit
import yaml
from homelab_pydantic import BaseModel, HomelabRootModel
from pulumi import Output, ResourceOptions
from pydantic import TypeAdapter, model_validator

from ...model.container.volume_path import ContainerVolumePath
from ..volume import VolumeResource
from . import FileResource

T = TypeVar("T", bound=BaseModel)


class JsonDefaultModel(HomelabRootModel[dict[str, Any]]):
    jsonschema: ClassVar[Any | None] = None

    root: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def validate_jsonschema(cls, data: Any) -> Any:
        if cls.jsonschema:
            jsonschema.validate(data, cls.jsonschema)
        return data


class ConfigDumper(Generic[T]):
    @staticmethod
    @abc.abstractmethod
    def dumps(data: T) -> str: ...

    @staticmethod
    @abc.abstractmethod
    def suffix() -> str: ...


class TomlDumper(ConfigDumper[T]):
    @staticmethod
    def dumps(data: T) -> str:
        return tomlkit.dumps(
            data.model_dump(
                mode="json", by_alias=True, exclude_unset=True, exclude_none=True
            ),
            sort_keys=True,
        )

    @staticmethod
    def suffix() -> str:
        return ".toml"


class IniDumper(ConfigDumper[T]):
    @staticmethod
    def dumps(data: T) -> str:
        parser = configparser.ConfigParser()
        for name, section in data.model_dump(by_alias=True).items():
            parser.add_section(name)
            for option, value in (
                TypeAdapter(dict[str, str]).validate_python(section).items()
            ):
                parser.set(name, option, value)
        config_content = io.StringIO()
        parser.write(config_content)
        config_content.seek(0)

        return config_content.read()

    @staticmethod
    def suffix() -> str:
        return ".conf"


class YamlDumper(ConfigDumper[T]):
    @staticmethod
    def dumps(data: T) -> str:
        return yaml.dump(
            data.model_dump(
                mode="json", by_alias=True, exclude_unset=True, exclude_none=True
            ),
            default_flow_style=False,
            sort_keys=True,
        )

    @staticmethod
    def suffix() -> str:
        return ".yaml"


class ConfigFileResource(Generic[T], FileResource):
    validator: type[T]
    dumper: type[ConfigDumper[T]]
    suffix: str | None = None

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        volume_path: ContainerVolumePath,
        data: Mapping[str, Any],
        volume_resource: VolumeResource,
    ) -> None:
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=volume_path.with_suffix(self.suffix or self.dumper.suffix()),
            content=Output.json_dumps(data).apply(self.dumps),
            mode=0o444,
            volume_resource=volume_resource,
        )

    def validate(self, raw_data: str) -> T:
        return self.validator.model_validate_json(raw_data)

    def dumps(self, raw_data: str) -> str:
        return self.dumper.dumps(self.validate(raw_data))
