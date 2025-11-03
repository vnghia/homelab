from collections import defaultdict
from functools import cached_property

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from homelab_vpn.config.host import HostVpnConfig
from pydantic_extra_types.timezone_name import TimeZoneName

from ...config.docker import DockerConfig
from ...config.service import ServiceConfigBase
from ...config.service.database import ServiceDatabaseConfig
from ...model.docker.container.network import ContainerNetworkContainerConfig
from ...model.docker.container.ports import ContainerPortsConfig
from ...model.host.ip import HostIpModel
from ...model.service import ServiceModel
from .access import HostAccessModel


class HostNoServiceModel(HomelabBaseModel):
    access: HostAccessModel
    timezone: TimeZoneName
    ip: HostIpModel = HostIpModel()
    vpn: HostVpnConfig | None = None
    docker: DockerConfig
    variables: dict[str, GlobalExtract] = {}

    @property
    def vpn_(self) -> HostVpnConfig:
        if not self.vpn:
            raise ValueError("Host vpn config is not provided")
        return self.vpn


class HostServiceModelModel(HostNoServiceModel):
    name: str
    services: dict[str, ServiceModel]

    @cached_property
    def databases(self) -> dict[str, ServiceDatabaseConfig]:
        return {
            name: service.databases
            for name, service in self.services.items()
            if service.databases
        }

    @cached_property
    def ports(self) -> dict[str, dict[str | None, ContainerPortsConfig]]:
        ports: defaultdict[str, dict[str | None, ContainerPortsConfig]] = defaultdict(
            lambda: defaultdict(ContainerPortsConfig)
        )
        for (
            service_name,
            service_model,
        ) in self.services.items():
            for container_model in service_model.containers.values():
                network_mode = container_model.network.root
                if isinstance(network_mode, ContainerNetworkContainerConfig):
                    ports[network_mode.service or service_name][
                        network_mode.container
                    ] |= container_model.ports.with_service(service_name, False)
        return ports


class HostModel[T: ServiceConfigBase](HostNoServiceModel):
    services: T

    def service_model(self, name: str) -> HostServiceModelModel:
        return HostServiceModelModel(
            name=name,
            services=self.services.services,
            **self.model_dump(exclude={"services"}),
        )
