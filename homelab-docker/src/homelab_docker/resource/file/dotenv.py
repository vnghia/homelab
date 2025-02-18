from typing import Mapping

from homelab_pydantic import HomelabRootModel
from pulumi import Input, ResourceOptions

from ...model.container.volume_path import ContainerVolumePath
from ..volume import VolumeResource
from .config import ConfigDumper, ConfigFileResource


class DotenvModel(HomelabRootModel[dict[str, str]]):
    pass


class DotenvDumper(ConfigDumper[DotenvModel]):
    @staticmethod
    def dumps(data: DotenvModel) -> str:
        return (
            "\n".join(
                '{}="{}"'.format(k, v.replace('"', '\\"')) for k, v in data.root.items()
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
    dumper = DotenvDumper

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        container_volume_path: ContainerVolumePath,
        envs: Mapping[str, Input[str]],
        volume_resource: VolumeResource,
    ):
        self.envs = envs
        super().__init__(
            resource_name,
            opts=opts,
            container_volume_path=container_volume_path,
            data=envs,
            volume_resource=volume_resource,
        )
