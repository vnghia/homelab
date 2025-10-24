from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from netaddr_pydantic import IPAddress
from pydantic import PositiveInt


class FrpServerConfig(HomelabBaseModel):
    addr: IPAddress
    port: PositiveInt
    token: str


class FrpConfig(HomelabBaseModel):
    path: GlobalExtract
    server: FrpServerConfig
    protocol: str
    pool: PositiveInt
