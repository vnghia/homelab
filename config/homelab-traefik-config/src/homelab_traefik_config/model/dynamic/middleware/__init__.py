from __future__ import annotations

from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from ..type import TraefikDynamicType


class TraefikDynamicMiddlewareUseModel(HomelabBaseModel):
    service: str | None = None
    name: str | None


class TraefikDynamicMiddlewareBuildModel(HomelabBaseModel):
    type: TraefikDynamicType = TraefikDynamicType.HTTP
    name: str | None = None
    data: Any
    plugin: str | None = None


class TraefikDynamicMiddlewareModel(
    HomelabRootModel[
        TraefikDynamicMiddlewareUseModel | TraefikDynamicMiddlewareBuildModel
    ]
):
    pass
