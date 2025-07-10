from typing import Any

from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import Input

from .docker import DaguDagStepDockerExecutorModel
from .http import DaguDagStepHttpExecutorModel
from .jq import DaguDagStepJqExecutorModel


class DaguDagStepExecutorModel(
    HomelabRootModel[
        DaguDagStepDockerExecutorModel
        | DaguDagStepHttpExecutorModel
        | DaguDagStepJqExecutorModel
    ]
):
    def to_executor(
        self,
        main_service: ServiceResourceBase,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return self.root.to_executor(main_service, dotenvs)
