from typing import Any

from hatchet_sdk import Context, EmptyModel, Hatchet  # noqa: F401
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool import constant  # noqa: F401
from homelab_hatchet_tool.config import Config, ConfigDependency  # noqa: F401
from homelab_hatchet_tool.docker import Docker  # noqa: F401
from homelab_hatchet_tool.docker.model.exec import (
    DockerContainerExecConfig,  # noqa: F401
)
from homelab_hatchet_tool.docker.model.run import DockerContainerRunConfig  # noqa: F401


def build_workflows(hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
    return []
