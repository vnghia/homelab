from typing import Any

from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import Input

from .docker import DaguDagStepDockerExecutorModel


class DaguDagStepExecutorModel(HomelabRootModel[DaguDagStepDockerExecutorModel]):
    root: DaguDagStepDockerExecutorModel

    def to_executor(
        self,
        main_service: ServiceResourceBase,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return self.root.to_executor(main_service, dotenvs)
