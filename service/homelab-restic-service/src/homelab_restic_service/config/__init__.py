from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract


class ResticConfig(DaguServiceConfigBase):
    image: str
    configuration_dir: GlobalExtract
    cache_dir: GlobalExtract

    hostname: GlobalExtract
