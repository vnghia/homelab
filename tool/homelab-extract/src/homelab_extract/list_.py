from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from homelab_extract import GlobalExtract


class GlobalExtractListSource(HomelabBaseModel):
    list_: list[GlobalExtract]
