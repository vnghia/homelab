from typing import Any

from homelab_pydantic import HomelabBaseModel


class GlobalExtractJsonSource(HomelabBaseModel):
    json_: Any
