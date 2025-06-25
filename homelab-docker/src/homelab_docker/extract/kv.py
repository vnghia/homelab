from __future__ import annotations

import json
import secrets
import typing
from typing import ClassVar, Never

from homelab_extract.kv import GlobalExtractKvSource
from homelab_pydantic import HomelabRootModel
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalKvSourceExtractor(HomelabRootModel[GlobalExtractKvSource]):
    EXTRACTOR_KEY: ClassVar[str] = "__kv_extractor"
    EXTRACTOR_VALUE: ClassVar[str] = secrets.token_hex(16)

    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> Output[str]:
        from . import GlobalExtractor

        root = self.root
        return Output.json_dumps(
            {
                key: GlobalExtractor(value).extract_str(main_service, model)
                for key, value in root.kv.items()
            }
            | {self.EXTRACTOR_KEY: Output.from_input(self.EXTRACTOR_VALUE)}
        )

    def extract_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract path from kv source")

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from kv source")

    @classmethod
    def parse(cls, value: str) -> dict[str, str] | str:
        try:
            data = json.loads(value)
            if (
                isinstance(data, dict)
                and data.get(cls.EXTRACTOR_KEY) == cls.EXTRACTOR_VALUE
            ):
                return data
            return value
        except json.JSONDecodeError:
            return value
