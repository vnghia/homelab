from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel
from pydantic import HttpUrl, NonNegativeInt

if typing.TYPE_CHECKING:
    from . import PlainArgs


class GlobalPlainExtractTypeSource(
    HomelabRootModel[NonNegativeInt | bool | HttpUrl | str]
):
    def extract_str(self, plain_args: PlainArgs) -> str:
        root = self.root
        if isinstance(root, bool):
            return str(root).lower()
        return str(root)
