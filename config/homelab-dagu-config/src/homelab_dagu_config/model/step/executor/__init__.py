from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
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
        extractor_args: ExtractorArgs,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        return self.root.to_executor(extractor_args, dotenvs)
