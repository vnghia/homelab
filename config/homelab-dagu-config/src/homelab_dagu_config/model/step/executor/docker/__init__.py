from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_pydantic import HomelabRootModel
from pulumi import Input

from .exec import DaguDagStepDockerExecExecutorModel
from .run import DaguDagStepDockerRunExecutorModel


class DaguDagStepDockerExecutorModel(
    HomelabRootModel[
        DaguDagStepDockerRunExecutorModel | DaguDagStepDockerExecExecutorModel
    ]
):
    root: DaguDagStepDockerRunExecutorModel | DaguDagStepDockerExecExecutorModel

    def to_executor(
        self,
        extractor_args: ExtractorArgs,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Input[Any]]:
        root = self.root
        return {
            "type": "docker",
            "config": root.to_executor_config(extractor_args, dotenvs)
            if isinstance(root, DaguDagStepDockerRunExecutorModel)
            else root.to_executor_config(extractor_args),
        }
