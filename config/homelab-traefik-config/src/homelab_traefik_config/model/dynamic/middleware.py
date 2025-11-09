from __future__ import annotations

from enum import StrEnum, auto
from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class TraefikDynamicMiddlewareType(StrEnum):
    HTTP = auto()
    TCP = auto()


class TraefikDynamicMiddlewareUseModel(HomelabBaseModel):
    service: str | None = None
    name: str | None


class TraefikDynamicMiddlewareBuildModel(HomelabBaseModel):
    type: TraefikDynamicMiddlewareType = TraefikDynamicMiddlewareType.HTTP
    name: str | None = None
    data: Any
    plugin: str | None = None


class TraefikDynamicMiddlewareModel(
    HomelabRootModel[
        TraefikDynamicMiddlewareUseModel | TraefikDynamicMiddlewareBuildModel
    ]
):
    pass
