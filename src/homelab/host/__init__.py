from abc import abstractmethod

from homelab_dagu_service import DaguService
from homelab_docker.config.host import HostServiceModelConfig
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.host import HostResourceBase
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from homelab_global import GlobalArgs
from homelab_network.resource.network import NetworkResource
from homelab_traefik_service import TraefikService
from pulumi import ResourceOptions
from pydantic.alias_generators import to_snake

from ..file import File


class HostBase[T: ServiceConfigBase](HostResourceBase):
    def __init__(
        self,
        service: T,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
    ) -> None:
        super().__init__(
            opts=opts,
            global_args=global_args,
            network_resource=network_resource,
            config=config,
        )

        self.services_config = service

    def build_extra_services(self) -> None:
        self.extra_services = {
            service: type(
                "{}Service".format(service.capitalize()), (ExtraService,), {}
            )(model, opts=self.child_opts, extractor_args=self.extractor_args).build()
            for service, model in ExtraService.sort_depends_on(
                self.services_config.extra(ServiceWithConfigModel[ExtraConfig])
            ).items()
        }

    def build_file(self) -> None:
        self.file = File(
            opts=self.child_opts,
            traefik_service=self.traefik_service,
            dagu_service=self.dagu_service,
        )

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Host")).replace("_", "-")

    @property
    def traefik_service(self) -> TraefikService | None:
        return None

    @property
    def dagu_service(self) -> DaguService | None:
        return None
