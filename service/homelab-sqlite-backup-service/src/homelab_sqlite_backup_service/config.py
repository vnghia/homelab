from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract.service import ServiceExtract


class SqliteBackupConfig(DaguServiceConfigBase):
    source_dir: ServiceExtract
