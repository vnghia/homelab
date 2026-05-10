from typing import Any

from hatchet_sdk import Context, EmptyModel, Hatchet  # noqa: F401
from hatchet_sdk.runnables.workflow import BaseWorkflow
from homelab_hatchet_tool.config import Config  # noqa: F401
from homelab_hatchet_tool.docker import Docker  # noqa: F401
from homelab_hatchet_tool.docker.model.run import DockerContainerRunModel  # noqa: F401
from homelab_hatchet_tool.worker import label  # noqa: F401


def build_workflows(hatchet: Hatchet) -> list[BaseWorkflow[Any]]:
    return []
