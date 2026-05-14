from typing import Self

from homelab_pydantic import HomelabRootModel

from ...model.docker.plugin import PluginModel


class PluginConfig(HomelabRootModel[dict[str, PluginModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})
