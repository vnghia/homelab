from typing import Any, ClassVar, Self, Type

import deepmerge
import pulumi
from homelab_docker.config.docker import DockerConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_integration.config.integration import IntegrationConfig
from homelab_network.config.network import NetworkConfig
from pydantic import BaseModel

from .constant import PROJECT_LABELS, PROJECT_NAME, PROJECT_STACK


class Config[T: ServiceConfigBase](BaseModel):
    PROJECT_NAME: ClassVar[str] = PROJECT_NAME
    PROJECT_STACK: ClassVar[str] = PROJECT_STACK
    PROJECT_LABELS: ClassVar[dict[str, str]] = PROJECT_LABELS

    docker: DockerConfig[T]
    network: NetworkConfig
    integration: IntegrationConfig

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
            network=NetworkConfig(**cls.get_key("network")),
            integration=IntegrationConfig(**cls.get_key("integration")),
        )
