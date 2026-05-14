import typing
from typing import Self

from homelab_pydantic import HomelabRootModel

from ...model.user import UidGidModel

if typing.TYPE_CHECKING:
    from ..user import UidGidConfig


class ServiceUserConfig(HomelabRootModel[str | None | UidGidModel]):
    @classmethod
    def default(cls) -> Self:
        return cls(None)

    def model(self, users: UidGidConfig) -> UidGidModel:
        root = self.root
        if isinstance(root, UidGidModel):
            return root
        return users[root]
