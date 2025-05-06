from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import IPvAnyAddress, PositiveInt


class FrpServerConfig(HomelabBaseModel):
    addr: IPvAnyAddress
    port: PositiveInt
    token: str


class FrpConfig(HomelabBaseModel):
    path: GlobalExtract
    server: FrpServerConfig
    protocol: str
    pool: PositiveInt
