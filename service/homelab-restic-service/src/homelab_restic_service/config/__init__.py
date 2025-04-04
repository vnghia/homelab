from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract.service import ServiceExtract

from .database import ResticDatabaseConfig
from .keep import ResticKeepConfig


class ResticConfig(DaguServiceConfigBase):
    image: str
    profile_dir: ServiceExtract
    cache_dir: ServiceExtract

    password: ServiceExtract
    keep: ResticKeepConfig

    database: ResticDatabaseConfig
