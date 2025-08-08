from homelab_pydantic import HomelabBaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from ..model.platform import Platform
from ..model.service import ServiceModel


class HostConfig(HomelabBaseModel):
    user: str
    address: str
    platform: Platform
    timezone: TimeZoneName

    @property
    def ssh(self) -> str:
        return "ssh://{}@{}".format(self.user, self.address)


class HostServiceModelConfig(HostConfig):
    services: dict[str, ServiceModel]
