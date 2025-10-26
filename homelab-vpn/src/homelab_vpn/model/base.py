from __future__ import annotations

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict
from pydantic import PositiveInt


class VpnPortsModel(HomelabServiceConfigDict[PositiveInt]):
    NONE_KEY = "port"


class VpnBaseModel(HomelabBaseModel):
    ports: VpnPortsModel
    envs: dict[str, GlobalExtract] = {}

    def to_parent(self) -> VpnBaseModel:
        return VpnBaseModel(ports=self.ports, envs=self.envs)
