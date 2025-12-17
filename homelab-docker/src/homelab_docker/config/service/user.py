from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel

from ...model.user import UidGidModel

if typing.TYPE_CHECKING:
    from ..user import UidGidConfig


class ServiceUserConfig(HomelabRootModel[str | None | UidGidModel]):
    root: str | UidGidModel | None = None

    def model(self, users: UidGidConfig) -> UidGidModel:
        root = self.root
        if isinstance(root, UidGidModel):
            return root
        return users[root]
