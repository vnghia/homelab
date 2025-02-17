from typing import Any

from homelab_docker.resource.service import ServiceResourceBase
from pulumi import Input
from pydantic import BaseModel


class DaguDagStepDockerExecExecutorModel(BaseModel):
    container: str | None

    def to_executor_config[T](
        self,
        main_service: ServiceResourceBase[T],
    ) -> dict[str, Input[Any]]:
        return {"containerName": main_service.containers[self.container].name}
