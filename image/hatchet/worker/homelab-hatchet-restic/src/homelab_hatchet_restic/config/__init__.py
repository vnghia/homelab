from typing import Any

from homelab_pydantic import HomelabBaseModel


class ResticConfig(HomelabBaseModel):
    container: dict[str, Any]
