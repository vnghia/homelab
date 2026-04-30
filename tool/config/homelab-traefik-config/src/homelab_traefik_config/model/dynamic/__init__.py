from homelab_pydantic import HomelabRootModel

from .http import TraefikDynamicHttpModel
from .middleware import TraefikDynamicMiddlewareBuildModel
from .tcp import TraefikDynamicTcpModel


class TraefikDynamicModel(
    HomelabRootModel[
        TraefikDynamicHttpModel
        | TraefikDynamicTcpModel
        | TraefikDynamicMiddlewareBuildModel
    ]
):
    @property
    def active(self) -> bool:
        root = self.root
        if isinstance(root, (TraefikDynamicHttpModel, TraefikDynamicTcpModel)):
            return root.active
        return True
