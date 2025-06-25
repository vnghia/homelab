from __future__ import annotations

import typing

from homelab_pydantic import HomelabBaseModel

if typing.TYPE_CHECKING:
    from . import GlobalExtract


class GlobalExtractKvSource(HomelabBaseModel):
    kv: dict[str, "GlobalExtract"]
