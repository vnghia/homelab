from homelab_config import constant
from homelab_docker.model.service import Model as ServiceModel
from homelab_docker.resource.global_ import Global as GlobalResource
from homelab_docker.resource.service import Args as ServiceArgs
from pulumi import ComponentResource, ResourceOptions
from pydantic import BaseModel
from pydantic_extra_types.timezone_name import TimeZoneName

from .dozzle import Dozzle

# class Service(ComponentResource):
#     RESOURCE_NAME = "service"

#     def __init__(
#         self,
#         resource: Resource,
#         opts: ResourceOptions | None,
#     ) -> None:
#         super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
#         self.child_opts = ResourceOptions(parent=self)

#         self.tailscale = Tailscale(resource=resource, opts=self.child_opts)
#         self.traefik = Traefik(
#             resource=resource, tailscale=self.tailscale, opts=self.child_opts
#         )
#         self.nghe = Nghe(
#             resource=resource, traefik=self.traefik.static, opts=self.child_opts
#         )

#         self.register_outputs({})


class Config(BaseModel):
    dozzle: ServiceModel[None]


class Service(ComponentResource):
    RESOURCE_NAME = "service"

    def __init__(
        self,
        config: Config,
        *,
        timezone: TimeZoneName,
        global_resource: GlobalResource,
        opts: ResourceOptions | None,
    ) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts)
        self.child_opts = ResourceOptions(parent=self)

        self.args = ServiceArgs(
            timezone=timezone,
            global_resource=global_resource,
            opts=self.child_opts,
            project_labels=constant.PROJECT_LABELS,
        )

        self.dozzle = Dozzle(config.dozzle, args=self.args)
