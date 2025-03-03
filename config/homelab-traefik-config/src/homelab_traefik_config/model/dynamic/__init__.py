from homelab_pydantic import HomelabRootModel

from .http import TraefikDynamicHttpModel
from .middleware import TraefikDynamicMiddlewareBuildModel


class TraefikDynamicModel(
    HomelabRootModel[TraefikDynamicHttpModel | TraefikDynamicMiddlewareBuildModel]
):
    pass
