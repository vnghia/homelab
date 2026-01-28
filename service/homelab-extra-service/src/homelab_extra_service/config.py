from homelab_dagu_config import DaguServiceConfigBase
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import ConfigDict


class ExtraConfig(TraefikServiceConfigBase, DaguServiceConfigBase):
    model_config = ConfigDict(extra="allow")
