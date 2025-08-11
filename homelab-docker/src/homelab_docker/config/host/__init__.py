from homelab_pydantic import HomelabRootModel

from ...model.host import HostServiceModelModel


class HostServiceModelConfig(HomelabRootModel[dict[str, HostServiceModelModel]]):
    def __getitem__(self, key: str) -> HostServiceModelModel:
        return self.root[key]
