from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel


class CrowdsecDockerConfig(HomelabBaseModel):
    acquis_dir: GlobalExtract
    check_interval: str


class CrowdsecConfig(HomelabBaseModel):
    docker: CrowdsecDockerConfig
