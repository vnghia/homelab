from typing import Any

from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import Input


class DaguDagStepDockerExecExecutorModel(HomelabBaseModel):
    container: str | None

    def to_executor_config(
        self,
        main_service: ServiceResourceBase,
    ) -> dict[str, Input[Any]]:
        return {"containerName": main_service.containers[self.container].name}
