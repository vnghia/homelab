from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_pydantic import HomelabBaseModel
from pulumi import Input


class DaguDagStepDockerExecExecutorModel(HomelabBaseModel):
    container: str | None

    def to_executor_config(
        self, extractor_args: ExtractorArgs
    ) -> dict[str, Input[Any]]:
        return {"containerName": extractor_args.service.containers[self.container].name}
