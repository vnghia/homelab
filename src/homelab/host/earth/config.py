from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel


class EarthServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel
