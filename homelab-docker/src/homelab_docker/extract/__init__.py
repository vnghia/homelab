from __future__ import annotations

import dataclasses
import typing
from typing import Any, Protocol, Self, TypeVar

import pulumi_random as random
from homelab_global import GlobalArgs
from homelab_network.model.hostname import Hostnames
from homelab_pydantic import AbsolutePath
from pulumi import Output
from pydantic import IPvAnyNetwork

if typing.TYPE_CHECKING:
    from ..config.host import HostServiceModelConfig
    from ..model.docker.container import ContainerModel
    from ..model.docker.container.volume_path import ContainerVolumePath
    from ..model.host import HostServiceModelModel
    from ..model.service import ServiceModel
    from ..resource.docker.container import ContainerResource
    from ..resource.host import HostResourceBase
    from ..resource.service import ServiceResourceBase


@dataclasses.dataclass(frozen=True)
class ExtractorArgs:
    global_args: GlobalArgs
    hostnames: Hostnames
    config: HostServiceModelConfig
    _host: HostResourceBase | HostServiceModelModel | None
    _service: ServiceResourceBase | ServiceModel | None
    _container: ContainerResource | ContainerModel | None

    @classmethod
    def from_host(
        cls,
        global_args: GlobalArgs,
        hostnames: Hostnames,
        config: HostServiceModelConfig,
        host: HostResourceBase,
    ) -> Self:
        return cls(
            global_args=global_args,
            hostnames=hostnames,
            config=config,
            _host=host,
            _service=None,
            _container=None,
        )

    def from_service(
        self, service: ServiceResourceBase, container: str | None = None
    ) -> Self:
        return self.__class__(
            global_args=self.global_args,
            hostnames=self.hostnames,
            config=self.config,
            _host=self._host,
            _service=service,
            _container=service.containers.get(
                container, service.container_models.get(container)
            ),
        )

    @property
    def host(self) -> HostResourceBase:
        from ..resource.host import HostResourceBase

        if not self._host or not isinstance(self._host, HostResourceBase):
            raise ValueError("Host is required for this extractor")
        return self._host

    @property
    def host_model(self) -> HostServiceModelModel:
        from ..model.host import HostServiceModelModel

        if not self._host:
            raise ValueError("Host or host model is required for this extractor")
        if isinstance(self._host, HostServiceModelModel):
            return self._host
        return self._host.model

    @property
    def services(self) -> dict[str, ServiceResourceBase]:
        return self.host.services

    @property
    def service(self) -> ServiceResourceBase:
        from ..resource.service import ServiceResourceBase

        if not self._service or not isinstance(self._service, ServiceResourceBase):
            raise ValueError("Service is required for this extractor")
        return self._service

    @property
    def service_model(self) -> ServiceModel:
        from ..model.service import ServiceModel

        if not self._service:
            raise ValueError("Service or service model is required for this extractor")
        if isinstance(self._service, ServiceModel):
            return self._service
        return self._service.model

    @property
    def container(self) -> ContainerResource:
        from ..resource.docker.container import ContainerResource

        if not self._container or not isinstance(self._container, ContainerResource):
            raise ValueError("Container is required for this extractor")
        return self._container

    @property
    def container_model(self) -> ContainerModel:
        from ..model.docker.container import ContainerModel

        if not self._container:
            raise ValueError(
                "Container or container model is required for this extractor"
            )
        if isinstance(self._container, ContainerModel):
            return self._container
        return self._container.model

    def get_host(self, key: str | None) -> HostResourceBase | HostServiceModelModel:
        from ..resource.host import HostResourceBase

        if not key:
            if not self._host:
                raise ValueError("Host or host model is required for this extractor")
            return self._host
        return HostResourceBase.HOSTS.get(key, self.config[key])

    def get_host_model(self, key: str | None) -> HostServiceModelModel:
        from ..resource.host import HostResourceBase

        host = self.get_host(key)
        if isinstance(host, HostResourceBase):
            return host.model
        return host

    def get_service(self, key: str | None) -> ServiceResourceBase | ServiceModel:
        from ..resource.host import HostResourceBase

        if not key:
            if not self._service:
                raise ValueError(
                    "Service or service model is required for this extractor"
                )
            return self._service
        if not self._host:
            raise ValueError("Host or host model is required for this extractor")
        if isinstance(self._host, HostResourceBase):
            return self._host.services.get(key, self._host.model.services[key])
        return self._host.services[key]

    def get_container(self, key: str | None) -> ContainerResource | ContainerModel:
        from ..resource.service import ServiceResourceBase

        if not self._service:
            raise ValueError("Service or service model is required for this extractor")
        if isinstance(self._service, ServiceResourceBase):
            if key in self._service.containers:
                return self._service.containers[key]
            return self._service.model[key]
        return self._service[key]

    def with_host(self, host: HostResourceBase | HostServiceModelModel | None) -> Self:
        from ..resource.host import HostResourceBase

        same_host = (
            isinstance(host, HostResourceBase)
            and isinstance(self._host, HostResourceBase)
            and host.name() == self._host.name()
        ) or (host is None)

        return self.__class__(
            global_args=self.global_args,
            hostnames=self.hostnames,
            config=self.config,
            _host=host or self._host,
            # Clear the service if the host has changed
            _service=self._service if same_host else None,
            # Clear the container if the host has changed
            _container=self._container if same_host else None,
        )

    def with_service(self, service: ServiceResourceBase | ServiceModel | None) -> Self:
        from ..resource.service import ServiceResourceBase

        return self.__class__(
            global_args=self.global_args,
            hostnames=self.hostnames,
            config=self.config,
            _host=self._host,
            _service=service or self._service,
            # Clear the container if the service has changed
            _container=self._container
            if (
                (
                    isinstance(service, ServiceResourceBase)
                    and isinstance(self._service, ServiceResourceBase)
                    and service.name() == self._service.name()
                )
                or (service is None)
            )
            else None,
        )

    def with_container(
        self, container: ContainerResource | ContainerModel | None
    ) -> Self:
        return self.__class__(
            global_args=self.global_args,
            hostnames=self.hostnames,
            config=self.config,
            _host=self._host,
            _service=self._service,
            _container=container or self._container,
        )


T = TypeVar("T")


class ExtractorBase(Protocol[T]):
    root: T

    def __init__(self, root: T) -> None:
        self.root = root

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> (
        str
        | Output[str]
        | dict[str, Output[str]]
        | random.RandomPassword
        | dict[Output[str], Any]
        | list[Output[IPvAnyNetwork]]
    ):
        raise TypeError("Could not extract str from {}".format(self.name))

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        raise TypeError("Could not extract path from {}".format(self.name))

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        raise TypeError("Could not extract volume path from {}".format(self.name))
