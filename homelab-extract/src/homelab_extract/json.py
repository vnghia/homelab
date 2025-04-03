from __future__ import annotations

from typing import Any

from homelab_pydantic import HomelabBaseModel


class GlobalExtractJsonSource(HomelabBaseModel):
    json_: Any
