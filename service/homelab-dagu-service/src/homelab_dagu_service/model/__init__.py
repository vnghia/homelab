from __future__ import annotations

import typing
from typing import Any

from homelab_dagu_config.model import DaguDagModel
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from ..model.params import DaguDagParamsModelBuilder
from .step import DaguDagStepModelBuilder

if typing.TYPE_CHECKING:
    from .. import DaguService
    from ..resource import DaguDagResource


class DaguDagModelBuilder(HomelabRootModel[DaguDagModel]):
    def to_data(
        self,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
        log_dir: ContainerVolumePath | None,
    ) -> dict[str, Any]:
        root = self.root
        dagu_config = dagu_service.config

        dotenvs = (
            [
                dagu_service.dotenvs[main_service.name()][dotenv]
                for dotenv in root.dotenvs
            ]
            if root.dotenvs
            else None
        )

        return {
            "dotenv": [
                dotenv.to_path(
                    dagu_service, dagu_service.model[dagu_config.dags_dir.container]
                )
                for dotenv in dotenvs
            ]
            if dotenvs
            else None,
            "name": main_service.add_service_name(root.name),
            "group": root.group or main_service.name(),
            "tags": root.tags,
            "logDir": log_dir.to_path(
                dagu_service, dagu_service.model[dagu_config.log_dir.container]
            )
            if log_dir
            else None,
            "schedule": root.schedule,
            "maxActiveRuns": root.max_active_runs,
            "params": DaguDagParamsModelBuilder(root.params).to_params(
                root, main_service
            )
            if root.params
            else None,
            "steps": [
                DaguDagStepModelBuilder(step).to_step(
                    root.params, main_service, dagu_service, dotenvs
                )
                for step in root.steps
            ],
        }

    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
    ) -> DaguDagResource:
        from ..resource import DaguDagResource

        resource = DaguDagResource(
            resource_name,
            self,
            opts=opts,
            main_service=main_service,
            dagu_service=dagu_service,
        )
        dagu_service.dags[main_service.name()][resource_name] = resource
        return resource
