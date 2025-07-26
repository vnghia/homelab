from typing import Mapping

from homelab_pydantic import HomelabRootModel
from pulumi import Input, ResourceOptions

from ...model.container.volume_path import ContainerVolumePath
from ..volume import VolumeResource
from .config import ConfigDumper, ConfigFileResource


class DotenvDumper(ConfigDumper[HomelabRootModel[dict[str, str]]]):
    @staticmethod
    def dumps(data: HomelabRootModel[dict[str, str]]) -> str:
        return (
            "\n".join(
                '{}="{}"'.format(k, v.replace('"', '\\"'))
                for k, v in sorted(data.root.items(), key=lambda x: x[0])
            )
            + "\n"
        )

    @staticmethod
    def suffix() -> str:
        return ".env"


class DotenvFileResource(
    ConfigFileResource[HomelabRootModel[dict[str, str]]], module="docker", name="Dotenv"
):
    validator = HomelabRootModel[dict[str, str]]
    dumper = DotenvDumper

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        volume_path: ContainerVolumePath,
        envs: Mapping[str, Input[str]],
        volume_resource: VolumeResource,
    ) -> None:
        self.envs = envs
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=volume_path,
            data=envs,
            volume_resource=volume_resource,
        )
