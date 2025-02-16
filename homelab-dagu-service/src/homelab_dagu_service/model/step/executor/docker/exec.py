from typing import Any

from homelab_docker.resource.service import ServiceResourceArgs
from pulumi import Input
from pydantic import BaseModel


class DaguDagStepDockerExecutorExecModel(BaseModel):
    container: str

    def to_executor_config(
        self, service_resource_args: ServiceResourceArgs
    ) -> dict[str, Input[Any]]:
        return {"containerName": service_resource_args.containers[self.container].name}
