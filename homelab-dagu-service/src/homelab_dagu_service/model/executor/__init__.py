from typing import Any

from homelab_docker.resource.service import ServiceResourceArgs
from pulumi import Input
from pydantic import RootModel

from .docker import DaguDagDockerExecutorModel


class DaguDagExecutorModel(RootModel[DaguDagDockerExecutorModel]):
    root: DaguDagDockerExecutorModel

    def to_executor(
        self, service_resource_args: ServiceResourceArgs
    ) -> dict[str, Input[Any]]:
        return self.root.to_executor(service_resource_args)
