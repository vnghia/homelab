from __future__ import annotations

from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class TraefikDynamicMiddlewareUseModel(HomelabBaseModel):
    service: str | None = None
    name: str | None


class TraefikDynamicMiddlewareBuildModel(HomelabBaseModel):
    name: str
    data: Any
    plugin: str | None = None


class TraefikDynamicMiddlewareModel(
    HomelabRootModel[
        TraefikDynamicMiddlewareUseModel | TraefikDynamicMiddlewareBuildModel
    ]
):
    pass
