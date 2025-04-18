from homelab_dagu_config import DaguServiceConfigBase
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel, HomelabServiceConfigDict
from homelab_s3_config import S3ServiceConfigBase
from homelab_traefik_config import TraefikServiceConfigBase
from pydantic import PositiveInt


class ExtraFile(HomelabBaseModel):
    path: GlobalExtract
    mode: PositiveInt = 0o444
    content: GlobalExtract


class ExtraFileConfig(HomelabServiceConfigDict[dict[str, ExtraFile]]):
    NONE_KEY = "file"


class ExtraConfig(TraefikServiceConfigBase, S3ServiceConfigBase, DaguServiceConfigBase):
    files: ExtraFileConfig = ExtraFileConfig({})
