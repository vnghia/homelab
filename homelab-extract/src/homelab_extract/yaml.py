from typing import Any

from homelab_pydantic import HomelabBaseModel


class GlobalExtractYamlSource(HomelabBaseModel):
    yaml: Any
