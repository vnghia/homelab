from typing import ClassVar, Type, TypeVar

import deepmerge
import pulumi
from pydantic import BaseModel

from homelab_config.constant import PROJECT_LABELS, PROJECT_NAME, PROJECT_STACK
from homelab_config.docker import Docker
from homelab_config.integration import Integration
from homelab_config.network import Network

KeyConfig = TypeVar("KeyConfig", bound=BaseModel)


class Config(BaseModel):
    PROJECT_NAME: ClassVar[str] = PROJECT_NAME
    PROJECT_STACK: ClassVar[str] = PROJECT_STACK
    PROJECT_LABELS: ClassVar[dict[str, str]] = PROJECT_LABELS

    docker: Docker
    network: Network
    integration: Integration

    @classmethod
    def build_key(cls, type_: Type[KeyConfig]) -> KeyConfig:
        key = type_.__name__.lower()
        return type_(
            **deepmerge.always_merger.merge(
                pulumi.Config().get_object(key, {}),
                pulumi.Config().get_object("stack-{}".format(key), {}),
            )
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


config = Config(
    docker=Config.build_key(Docker),
    network=Config.build_key(Network),
    integration=Config.build_key(Integration),
)
