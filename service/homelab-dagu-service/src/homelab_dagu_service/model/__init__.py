import typing
from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions
from pydantic import BaseModel, PositiveInt

from .params import DaguDagParamsModel
from .step import DaguDagStepModel

if typing.TYPE_CHECKING:
    from .. import DaguService
    from ..resource import DaguDagResource


class DaguDagModel(BaseModel):
    name: str | None = None
    path: str | None = None

    group: str | None = None
    tags: list[str] = []
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None
    params: DaguDagParamsModel | None = None

    steps: list[DaguDagStepModel]

    def to_data[T](
        self,
        main_service: ServiceResourceBase[T],
        dagu_service: "DaguService",
        build_args: ContainerModelBuildArgs | None,
        dotenv: DotenvFileResource | None,
    ) -> dict[str, Any]:
        return {
            "dotenv": dotenv.to_container_path(
                dagu_service.model.container.volumes
            ).as_posix()
            if dotenv
            else None,
            "name": self.name,
            "group": self.group,
            "tags": self.tags,
            "schedule": self.schedule,
            "maxActiveRuns": self.max_active_runs,
            "params": [{key: param} for key, param in self.params.root.items()]
            if self.params
            else None,
            "steps": [
                step.to_step(self.params, main_service, build_args, dotenv)
                for step in self.steps
            ],
        }

    def build_resource[T](
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase[T],
        dagu_service: "DaguService",
        build_args: ContainerModelBuildArgs | None,
        dotenv: DotenvFileResource | None,
    ) -> "DaguDagResource":
        from ..resource import DaguDagResource

        return DaguDagResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            dagu_service=dagu_service,
            build_args=build_args,
            dotenv=dotenv,
        )
