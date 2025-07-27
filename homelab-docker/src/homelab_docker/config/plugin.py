from homelab_pydantic import HomelabRootModel

from ..model.plugin import PluginModel


class PluginConfig(HomelabRootModel[dict[str, PluginModel]]):
    root: dict[str, PluginModel] = {}
