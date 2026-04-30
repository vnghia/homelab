from enum import StrEnum, auto
from typing import Any

from homelab_pydantic import HomelabBaseModel


class GlobalExtractConfigFormat(StrEnum):
    JSON = auto()
    YAML = auto()
    TOML = auto()


class GlobalExtractConfigSource(HomelabBaseModel):
    data: Any
    format: GlobalExtractConfigFormat
