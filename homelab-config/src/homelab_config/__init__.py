from pathlib import Path
from typing import Any, ClassVar, Self, Type

import deepmerge
import pulumi
import yaml
from homelab_docker.config import DockerConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_network.config.network import NetworkConfig
from homelab_pydantic import HomelabBaseModel

from .constant import PROJECT_LABELS, PROJECT_NAME, PROJECT_STACK


class Config[T: ServiceConfigBase](HomelabBaseModel):
    PROJECT_NAME: ClassVar[str] = PROJECT_NAME
    PROJECT_STACK: ClassVar[str] = PROJECT_STACK
    PROJECT_LABELS: ClassVar[dict[str, str]] = PROJECT_LABELS

    docker: DockerConfig[T]
    network: NetworkConfig

    @classmethod
    def get_key(cls, key: str) -> Any:
        data = pulumi.Config().get_object(key, {})

        for path in (
            (Path(__file__).parent.parent.parent.parent / "config" / key)
            .resolve(True)
            .glob("*.yaml")
        ):
            with open(path) as file:
                data = deepmerge.always_merger.merge(data, yaml.full_load(file))

        return deepmerge.always_merger.merge(
            data, pulumi.Config().get_object("stack-{}".format(key), {})
        )

    @classmethod
    def get_name(
        cls, name: str | None, project: bool = False, stack: bool = True
    ) -> str:
        return "-".join(
            ([cls.PROJECT_NAME] if project or not name else [])
            + ([name] if name else [])
            + ([cls.PROJECT_STACK] if stack else [])
        )

    @classmethod
    def build(cls, docker_type: Type[DockerConfig[T]]) -> Self:
        return cls(
            docker=docker_type(**cls.get_key("docker")),
            network=NetworkConfig(**cls.get_key("network")),
        )
