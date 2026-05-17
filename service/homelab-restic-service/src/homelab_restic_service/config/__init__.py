from homelab_extract import GlobalExtract
from homelab_hatchet_config import HatchetServiceConfigBase


class ResticConfig(HatchetServiceConfigBase):
    image: str
    configuration_dir: GlobalExtract
    cache_dir: GlobalExtract

    hostname: GlobalExtract
