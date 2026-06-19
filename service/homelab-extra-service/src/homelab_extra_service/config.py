from homelab_hatchet_config import HatchetServiceConfigBase
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import ConfigDict


class ExtraConfig(TraefikServiceConfigBase, HatchetServiceConfigBase):
    model_config = ConfigDict(extra="allow")
