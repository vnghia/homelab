import abc
import configparser
import io
from typing import Any, ClassVar, Generic, Mapping, TypeVar

import jsonschema
import rtoml
import yaml_rs
from homelab_pydantic import BaseModel, DictAdapter, HomelabRootModel
from pulumi import Output, ResourceOptions
from pydantic import model_validator

from ...extract import ExtractorArgs
from ...model.docker.container.volume_path import ContainerVolumePath
from ...model.file import FilePermissionModel
from ...model.user import UidGidModel
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
    @classmethod
    @abc.abstractmethod
    def dumps_any(cls, data: Any) -> str: ...

    @classmethod
    def dumps(cls, data: T) -> str:
        return cls.dumps_any(
            data.model_dump(
                mode="json", by_alias=True, exclude_unset=True, exclude_none=True
            )
        )

    @staticmethod
    @abc.abstractmethod
    def suffix() -> str: ...


class TomlDumper(ConfigDumper[T]):
    @classmethod
    def dumps_any(cls, data: Any) -> str:
        return rtoml.dumps(data, none_value=None)

    @staticmethod
    def suffix() -> str:
        return ".toml"


class IniDumper(ConfigDumper[T]):
    @classmethod
    def dumps_any(cls, data: Any) -> str:
        parser = configparser.ConfigParser()
        for name, section in data.items():
            parser.add_section(name)
            for option, value in DictAdapter.validate_python(section).items():
                parser.set(name, option, value)
        config_content = io.StringIO()
        parser.write(config_content)
        config_content.seek(0)

        return config_content.read()

    @staticmethod
    def suffix() -> str:
        return ".conf"


class YamlDumper(ConfigDumper[T]):
    @classmethod
    def dumps_any(cls, data: Any) -> str:
        return yaml_rs.dumps(data)

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
        opts: ResourceOptions,
        volume_path: ContainerVolumePath,
        data: Mapping[str, Any],
        permission: UidGidModel | FilePermissionModel,
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=volume_path.with_suffix(self.suffix or self.dumper.suffix()),
            content=Output.json_dumps(data).apply(self.dumps),
            permission=permission,
            extractor_args=extractor_args,
        )

    def validate(self, raw_data: str) -> T:
        return self.validator.model_validate_json(raw_data)

    def dumps(self, raw_data: str) -> str:
        return self.dumper.dumps(self.validate(raw_data))
