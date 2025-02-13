from pydantic import RootModel

from homelab_docker.model.plugin import PluginModel


class PluginConfig(RootModel[dict[str, PluginModel]]):
    root: dict[str, PluginModel]
