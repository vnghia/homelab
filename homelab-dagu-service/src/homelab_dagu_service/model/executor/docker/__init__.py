from typing import Any

from homelab_docker.resource.service import ServiceResourceArgs
from pulumi import Input
from pydantic import RootModel

from .exec import DaguDagDockerExecutorExecModel


class DaguDagDockerExecutorModel(RootModel[DaguDagDockerExecutorExecModel]):
    root: DaguDagDockerExecutorExecModel

    def to_executor(
        self, service_resource_args: ServiceResourceArgs
    ) -> dict[str, Input[Any]]:
        return {
            "type": "docker",
            "config": self.root.to_executor_config(service_resource_args),
        }
