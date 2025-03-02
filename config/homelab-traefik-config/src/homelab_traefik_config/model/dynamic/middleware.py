from __future__ import annotations

from typing import Any

from homelab_pydantic import HomelabBaseModel, HomelabRootModel


class TraefikDynamicMiddlewareFullModel(HomelabBaseModel):
    name: str
    data: Any
    plugin: str | None = None


class TraefikDynamicMiddlewareModel(
    HomelabRootModel[str | TraefikDynamicMiddlewareFullModel]
):
    pass
