from homelab_pydantic import HomelabRootModel

from .http import TraefikDynamicHttpModel
from .middleware import TraefikDynamicMiddlewareBuildModel


class TraefikDynamicModel(
    HomelabRootModel[TraefikDynamicHttpModel | TraefikDynamicMiddlewareBuildModel]
):
    @property
    def active(self) -> bool:
        root = self.root
        if isinstance(root, TraefikDynamicHttpModel):
            return root.active
        return True
