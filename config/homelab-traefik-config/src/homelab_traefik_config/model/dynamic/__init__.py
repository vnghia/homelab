from homelab_pydantic import HomelabRootModel

from .http import TraefikDynamicHttpModel
from .middleware import TraefikDynamicMiddlewareFullModel


class TraefikDynamicModel(
    HomelabRootModel[TraefikDynamicHttpModel | TraefikDynamicMiddlewareFullModel]
):
    pass
