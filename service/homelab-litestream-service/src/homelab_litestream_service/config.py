from typing import Any

from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract


class LitestreamConfig(DaguServiceConfigBase):
    path: GlobalExtract
    global_: Any
