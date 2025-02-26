from __future__ import annotations

import typing
from typing import Never

from homelab_pydantic import HomelabRootModel
from pydantic import PositiveInt

if typing.TYPE_CHECKING:
    from .....resource.service import ServiceResourceBase
    from ... import ContainerModel


class ContainerExtractSimpleSource(HomelabRootModel[bool | PositiveInt | str]):
    def extract_str(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> str:
        root = self.root
        if isinstance(root, bool):
            return str(root).lower()
        else:
            return str(root)

    def extract_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract path from simple source")

    def extract_volume_path(
        self, _model: ContainerModel, _main_service: ServiceResourceBase
    ) -> Never:
        raise TypeError("Can not extract volume path from simple source")
