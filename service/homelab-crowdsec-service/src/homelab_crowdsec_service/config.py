from homelab_docker.model.service.extract import ServiceExtract
from homelab_pydantic import HomelabBaseModel


class CrowdsecDockerConfig(HomelabBaseModel):
    acquis_dir: ServiceExtract
    check_interval: str


class CrowdsecConfig(HomelabBaseModel):
    docker: CrowdsecDockerConfig
