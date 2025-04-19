from __future__ import annotations

import typing
from pathlib import PosixPath
from typing import Never

from homelab_extract.simple import GlobalExtractSimpleSource
from homelab_pydantic import AbsolutePath, HomelabRootModel

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalSimpleSourceExtractor(HomelabRootModel[GlobalExtractSimpleSource]):
    def extract_str(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> str:
        root = self.root.root
        if isinstance(root, bool):
            return str(root).lower()
        return str(root)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return AbsolutePath(PosixPath(self.extract_str(main_service, model)))

    def extract_volume_path(
        self, _main_service: ServiceResourceBase, _model: ContainerModel | None
    ) -> Never:
        raise TypeError("Can not extract volume path from simple source")
