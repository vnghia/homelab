from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
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

    def to_executor[T](
        self,
        main_service: ServiceResourceBase[T],
        build_args: ContainerModelBuildArgs | None,
        dotenv: DotenvFileResource | None,
    ) -> dict[str, Input[Any]]:
        root = self.root
        return {
            "type": "docker",
            "config": root.to_executor_config(main_service, build_args, dotenv)
            if isinstance(root, DaguDagStepDockerRunExecutorModel)
            else root.to_executor_config(main_service),
        }
