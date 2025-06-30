from __future__ import annotations

import typing
from typing import Never

from homelab_extract.kv import GlobalExtractKvSource
from homelab_extract.transform.string import ExtractTransformString
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalKvSourceExtractor(HomelabRootModel[GlobalExtractKvSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        from .global_ import GlobalExtractor

        root = self.root
        return Output.json_dumps(
            {
                key: GlobalExtractor(value).extract_str(main_service, model)
                for key, value in root.kv.items()
            }
            | {
                ExtractTransformString.JSON_KEY: Output.from_input(
                    ExtractTransformString.JSON_VALUE
                )
            }
        )

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from kv source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from kv source")
