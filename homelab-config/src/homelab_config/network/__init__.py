from pydantic import BaseModel, ConfigDict, Field, IPvAnyAddress

from homelab_config.network.dns import DnsMap


class Network(BaseModel):
    model_config = ConfigDict(strict=True)

    public_ips: dict[str, IPvAnyAddress] = Field(alias="public-ips")
    dns: DnsMap = Field(alias="dns")
