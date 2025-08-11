from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract

from .database import ResticDatabaseConfig
from .keep import ResticKeepConfig


class ResticConfig(DaguServiceConfigBase):
    image: str
    profile_dir: GlobalExtract
    cache_dir: GlobalExtract

    password: GlobalExtract
    keep: ResticKeepConfig

    database: ResticDatabaseConfig
