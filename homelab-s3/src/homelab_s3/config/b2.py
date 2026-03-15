from homelab_pydantic import HomelabRootModel

from ..model.b2 import B2Model


class B2Config(HomelabRootModel[dict[str, B2Model]]):
    root: dict[str, B2Model] = {}

    def __getitem__(self, key: str) -> B2Model:
        return self.root[key]
