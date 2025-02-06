from typing import Any, ClassVar, Self, Type

import deepmerge
import pulumi
from homelab_docker.config.docker import Docker as DockerConfig
from pydantic import BaseModel

from homelab_config.integration import Integration
from homelab_config.network import Network

from .constant import PROJECT_LABELS, PROJECT_NAME, PROJECT_STACK


class Config[T: BaseModel](BaseModel):
    PROJECT_NAME: ClassVar[str] = PROJECT_NAME
    PROJECT_STACK: ClassVar[str] = PROJECT_STACK
    PROJECT_LABELS: ClassVar[dict[str, str]] = PROJECT_LABELS

    docker: DockerConfig[T]
    network: Network
    integration: Integration

    @classmethod
    def get_key(cls, key: str) -> Any:
        return deepmerge.always_merger.merge(
            pulumi.Config().get_object(key, {}),
            pulumi.Config().get_object("stack-{}".format(key), {}),
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
            network=Network(**cls.get_key("network")),
            integration=Integration(**cls.get_key("integration")),
        )
