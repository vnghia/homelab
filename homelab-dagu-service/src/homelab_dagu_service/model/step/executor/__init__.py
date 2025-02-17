from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import Input
from pydantic import RootModel

from .docker import DaguDagStepDockerExecutorModel


class DaguDagStepExecutorModel(RootModel[DaguDagStepDockerExecutorModel]):
    root: DaguDagStepDockerExecutorModel

    def to_executor[T](
        self,
        main_service: ServiceResourceBase[T],
        build_args: ContainerModelBuildArgs | None,
        dotenv: DotenvFileResource | None,
    ) -> dict[str, Input[Any]]:
        return self.root.to_executor(main_service, build_args, dotenv)
