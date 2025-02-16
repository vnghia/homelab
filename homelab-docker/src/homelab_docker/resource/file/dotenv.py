from typing import Mapping

from pulumi import Input, ResourceOptions
from pydantic import RootModel

from ...model.container.volume_path import ContainerVolumePath
from ..volume import VolumeResource
from .config import ConfigDumper, ConfigFileResource


class DotenvModel(RootModel[dict[str, str]]):
    pass


class DotenvDumper(ConfigDumper[DotenvModel]):
    @staticmethod
    def dumps(data: DotenvModel) -> str:
        return (
            "\n".join(
                '{}="{}"'.replace(k, v.replace('"', '\\"'))
                for k, v in data.root.items()
            )
            + "\n"
        )

    @staticmethod
    def suffix() -> str:
        return ".env"


class DotenvFileResource(
    ConfigFileResource[DotenvModel], module="docker", name="Dotenv"
):
    validator = DotenvModel
    dumper: type[ConfigDumper[DotenvModel]]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        container_volume_path: ContainerVolumePath,
        data: Mapping[str, Input[str]],
        volume_resource: VolumeResource,
    ):
        self.data = data
        super().__init__(
            resource_name,
            opts=opts,
            container_volume_path=container_volume_path,
            data=data,
            volume_resource=volume_resource,
        )
