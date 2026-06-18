from typing import Self

from homelab_pydantic import HomelabRootModel

from ..model.ovh import OvhModel


class OvhConfig(HomelabRootModel[dict[str, OvhModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})

    def __getitem__(self, key: str) -> OvhModel:
        return self.root[key]
