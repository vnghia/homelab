from typing import Any

from homelab_extract import GlobalExtract
from homelab_hatchet_config import HatchetServiceConfigBase


class LitestreamConfig(HatchetServiceConfigBase):
    path: GlobalExtract
    global_: Any
