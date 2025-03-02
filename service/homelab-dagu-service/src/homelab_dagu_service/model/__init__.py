from __future__ import annotations

import typing
from typing import Any

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabBaseModel
from pulumi import ResourceOptions
from pydantic import PositiveInt

from .params import DaguDagParamsModel
from .step import DaguDagStepModel

if typing.TYPE_CHECKING:
    from .. import DaguService
    from ..resource import DaguDagResource


class DaguDagModel(HomelabBaseModel):
    name: str | None = None
    path: str | None = None

    group: str | None = None
    tags: list[str] = []
    schedule: str | None = None
    max_active_runs: PositiveInt | None = None
    params: DaguDagParamsModel = DaguDagParamsModel()

    steps: list[DaguDagStepModel] = []

    def to_data(
        self,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
        log_dir: ContainerVolumePath | None,
        build_args: ContainerModelBuildArgs | None,
        dotenvs: list[DotenvFileResource] | None,
    ) -> dict[str, Any]:
        dagu_config = dagu_service.config

        return {
            "dotenv": [
                dotenv.to_path(dagu_service.model[dagu_config.dags_dir.container])
                for dotenv in dotenvs
            ]
            if dotenvs
            else None,
            "name": self.name,
            "group": self.group,
            "tags": self.tags,
            "logDir": log_dir.to_path(dagu_service.model[dagu_config.log_dir.container])
            if log_dir
            else None,
            "schedule": self.schedule,
            "maxActiveRuns": self.max_active_runs,
            "params": self.params.to_params(self) if self.params else None,
            "steps": [
                step.to_step(
                    self.params, main_service, dagu_service, build_args, dotenvs
                )
                for step in self.steps
            ],
        }

    def build_resource(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
        container_model_build_args: ContainerModelBuildArgs | None,
        dotenvs: list[DotenvFileResource] | None,
    ) -> DaguDagResource:
        from ..resource import DaguDagResource

        return DaguDagResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            dagu_service=dagu_service,
            container_model_build_args=container_model_build_args,
            dotenvs=dotenvs,
        )
