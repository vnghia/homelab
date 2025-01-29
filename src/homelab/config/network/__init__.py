from pydantic import BaseModel, ConfigDict

from homelab.config.network.dns import Dns


class Network(BaseModel):
    model_config = ConfigDict(strict=True)

    dns: dict[str, Dns]
