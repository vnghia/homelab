from __future__ import annotations

import dataclasses
import typing
from typing import Any, Protocol, Self, TypeVar

from homelab_pydantic import AbsolutePath
from pulumi import Output

if typing.TYPE_CHECKING:
    from ..model.container import ContainerModel
    from ..model.container.volume_path import ContainerVolumePath
    from ..model.service import ServiceModel
    from ..resource import DockerResourceArgs
    from ..resource.service import ServiceResourceBase


@dataclasses.dataclass(frozen=True)
class ExtractorArgs:
    _service: ServiceResourceBase | ServiceModel | None = None
    _container: ContainerModel | None = None

    @classmethod
    def from_service(
        cls, service: ServiceResourceBase, container: str | None = None
    ) -> Self:
        return cls(_service=service, _container=service.model.containers.get(container))

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
    def container(self) -> ContainerModel:
        if not self._container:
            raise ValueError("Container is required for this extractor")
        return self._container

    @property
    def docker_resource_args(self) -> DockerResourceArgs:
        return self.service.docker_resource_args

    def with_service(self, service: ServiceResourceBase | ServiceModel | None) -> Self:
        from ..resource.service import ServiceResourceBase

        return self.__class__(
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

    def with_container(self, container: ContainerModel | None) -> Self:
        return self.__class__(
            _service=self._service, _container=container or self._container
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
    ) -> str | Output[str] | dict[str, Output[str]] | dict[Output[str], Any]:
        raise TypeError("Could not extract str from {}".format(self.name))

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        raise TypeError("Could not extract path from {}".format(self.name))

    def extract_volume_path(self, extractor_args: ExtractorArgs) -> ContainerVolumePath:
        raise TypeError("Could not extract volume path from {}".format(self.name))
