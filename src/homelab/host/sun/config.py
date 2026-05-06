from homelab_docker.model.service import ServiceWithConfigModel
from homelab_kanidm_service.config import KandimConfig
from homelab_mail_service.config import MailConfig

from ..config import HostServiceConfig


class SunServiceConfig(HostServiceConfig):
    mail: ServiceWithConfigModel[MailConfig]
    kanidm: ServiceWithConfigModel[KandimConfig]
