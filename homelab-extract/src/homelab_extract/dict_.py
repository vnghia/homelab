from __future__ import annotations

import typing
from typing import Any

from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from . import GlobalExtract


class GlobalExtractDictSource(HomelabBaseModel):
    dict_: list[tuple["GlobalExtract", Any]]
