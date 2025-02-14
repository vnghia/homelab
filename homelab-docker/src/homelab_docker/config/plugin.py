from pydantic import RootModel

from ..model.plugin import PluginModel


class PluginConfig(RootModel[dict[str, PluginModel]]):
    root: dict[str, PluginModel]
