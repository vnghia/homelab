from enum import Enum

from pydantic import BaseModel, ConfigDict, PositiveInt
from pydantic_core import Url

# from homelab.docker.resource import Resource


class ServiceType(Enum):
    HTTP = "http"


class Service(BaseModel):
    model_config = ConfigDict(strict=True)

    container: str | None = None
    port: PositiveInt

    # def to_url(
    #     self,
    #     type_: ServiceType,
    #     router_name: str,
    #     resource: Resource,
    # ) -> Url:
    #     container = self.container or router_name
    #     resource.containers[container]
    #     return Url("{}://{}:{}".format(type.value, container, self.port))
