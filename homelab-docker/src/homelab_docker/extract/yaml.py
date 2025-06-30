from __future__ import annotations

import typing
from typing import Never

from homelab_extract.yaml import GlobalExtractYamlSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalYamlSourceExtractor(HomelabRootModel[GlobalExtractYamlSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        from ..resource.file.config import JsonDefaultModel, YamlDumper
        from .global_ import GlobalExtractor

        root = self.root
        return (
            Output.json_dumps(
                GlobalExtractor.extract_recursively(root.yaml, main_service, model)
            )
            .apply(JsonDefaultModel.model_validate_json)
            .apply(YamlDumper.dumps)
        )

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from yaml source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from yaml source")
