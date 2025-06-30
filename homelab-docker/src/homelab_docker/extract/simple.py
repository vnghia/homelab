from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_extract.simple import GlobalExtractSimpleSource
from homelab_pydantic import AbsolutePath

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..resource.service import ServiceResourceBase


class GlobalSimpleSourceExtractor(ExtractorBase[GlobalExtractSimpleSource]):
    def extract_str(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> str:
        root = self.root.root
        if isinstance(root, bool):
            return str(root).lower()
        return str(root)

    def extract_path(
        self, main_service: ServiceResourceBase, model: ContainerModel | None
    ) -> AbsolutePath:
        return AbsolutePath(PosixPath(self.extract_str(main_service, model)))
