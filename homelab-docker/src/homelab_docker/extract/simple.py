from __future__ import annotations

import typing
from pathlib import PosixPath
from typing import Never

from homelab_pydantic import AbsolutePath, HomelabRootModel
from pydantic import NonNegativeInt

if typing.TYPE_CHECKING:
    from ..resource.service import ServiceResourceBase


class GlobalExtractSimpleSource(HomelabRootModel[NonNegativeInt | bool | str]):
    def extract_str(self, _main_service: ServiceResourceBase) -> str:
        root = self.root
        if isinstance(root, bool):
            return str(root).lower()
        else:
            return str(root)

    def extract_path(self, main_service: ServiceResourceBase) -> AbsolutePath:
        return AbsolutePath(PosixPath(self.extract_str(main_service)))

    def extract_volume_path(self, _main_service: ServiceResourceBase) -> Never:
        raise TypeError("Can not extract volume path from simple source")
