from __future__ import annotations

import typing

from homelab_pydantic import HomelabRootModel

from ...user import UidGidModel

if typing.TYPE_CHECKING:
    from ....config.user import UidGidConfig


class ContainerUserConfig(HomelabRootModel[str | UidGidModel]):
    def model(self, users: UidGidConfig) -> UidGidModel:
        root = self.root
        if isinstance(root, UidGidModel):
            return root
        return users[root]
