from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceModel, ServiceWithConfigModel
from homelab_traefik_service.config import TraefikConfig


class EarthServiceConfig(ServiceConfigBase):
    tailscale: ServiceModel
    traefik: ServiceWithConfigModel[TraefikConfig]
