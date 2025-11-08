from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract.service import ServiceExtract


class BaliteConfig(DaguServiceConfigBase):
    root: str
    source_dir: ServiceExtract
