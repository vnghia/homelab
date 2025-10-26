from __future__ import annotations

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


class HostBaseNoConfig(HostResourceBase):
    HOST_BASES: dict[str, HostBaseNoConfig] = {}

    def __init__(
        self,
        *,
        opts: ResourceOptions | None,
        global_args: GlobalArgs,
        network_resource: NetworkResource,
        config: HostServiceModelConfig,
        extra_services_config: dict[str, ServiceWithConfigModel[ExtraConfig]],
    ) -> None:
        super().__init__(
            opts=opts,
            global_args=global_args,
            network_resource=network_resource,
            config=config,
        )

        self.extra_services_config = extra_services_config
        self.HOST_BASES[self.name()] = self

    def build_extra_service(self, service: str) -> None:
        if service in self.services:
            return

        model = self.extra_services_config[service]
        if model.depends_on:
            for depend in model.depends_on:
                depend_full = depend.to_full()
                (
                    self.HOST_BASES[depend_full.host] if depend_full.host else self
                ).build_extra_service(depend_full.service)

        type("{}Service".format(service.capitalize()), (ExtraService,), {})(
            model, opts=self.child_opts, extractor_args=self.extractor_args
        ).build()

    def build_final_services_before_file(self) -> None:
        return None

    def build_final_services_after_file(self) -> None:
        return None

    def build_file(self) -> None:
        self.file = File(
            opts=self.child_opts,
            traefik_service=self.traefik_service,
            dagu_service=self.dagu_service,
        )

    @classmethod
    def finalize(cls) -> None:
        for host in cls.HOST_BASES.values():
            for service in host.extra_services_config:
                host.build_extra_service(service)

        for host in cls.HOST_BASES.values():
            host.build_final_services_before_file()
            host.build_file()
            host.build_final_services_after_file()
            host.register_outputs({})

    @property
    def traefik_service(self) -> TraefikService | None:
        return None

    @property
    def dagu_service(self) -> DaguService | None:
        return None


class HostBase[T: ServiceConfigBase](HostBaseNoConfig):
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
            extra_services_config=service.extra(ServiceWithConfigModel[ExtraConfig]),
        )

        self.services_config = service
        self.build_initial_extra_services()

    def build_initial_extra_services(self) -> None:
        for service, model in self.services_config.services.items():
            if service in self.extra_services_config or not model.depends_on:
                continue
            for depend in model.depends_on:
                depend_full = depend.to_full()
                if depend_full.host:
                    raise ValueError(
                        "Building initial extra services does not support switching host"
                    )
                if depend_full.service not in self.extra_services_config:
                    raise ValueError(
                        "Building initial extra services only supports extra services"
                    )
                self.build_extra_service(depend_full.service)

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Host")).replace("_", "-")
