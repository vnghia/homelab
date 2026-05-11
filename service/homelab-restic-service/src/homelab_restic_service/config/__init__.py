from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract
from homelab_hatchet_config import HatchetServiceConfigBase


class ResticConfig(DaguServiceConfigBase, HatchetServiceConfigBase):
    image: str
    configuration_dir: GlobalExtract
    cache_dir: GlobalExtract

    hostname: GlobalExtract
