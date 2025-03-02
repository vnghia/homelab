from __future__ import annotations

import typing

import pulumi_random as random
from homelab_pydantic import AbsolutePath, HomelabBaseModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ...model.container import ContainerModel
    from ...model.container.volume_path import ContainerVolumePath
    from ...resource.service import ServiceResourceBase
    from .. import GlobalExtract


class ServiceExtractVariableSource(HomelabBaseModel):
    variable: str

    def get_variable(self, main_service: ServiceResourceBase) -> GlobalExtract:
        return main_service.model.variables[self.variable]

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str | Output[str] | random.RandomPassword:
        return self.get_variable(main_service).extract_str(main_service, model)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return self.get_variable(main_service).extract_path(main_service, model)

    def extract_volume_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> ContainerVolumePath:
        return self.get_variable(main_service).extract_volume_path(main_service, model)
