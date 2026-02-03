from typing import Any

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.host import ContainerHostModeConfig
from homelab_docker.model.docker.container.network import (
    ContainerNetworkContainerConfig,
    ContainerNetworkMode,
    ContainerNetworkModeConfig,
)
from homelab_docker.resource.service import ServiceResourceBase
from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabRootModel
from homelab_traefik_config.model.dynamic.service import (
    TraefikDynamicServiceFullModel,
    TraefikDynamicServiceModel,
)
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
from pulumi import Output
from pydantic import PositiveInt, TypeAdapter


class TraefikDynamicServiceFullModelBuilder(
    HomelabRootModel[TraefikDynamicServiceFullModel]
):
    def get_service_name(
        self, container_name: str | None, service: ServiceResourceBase
    ) -> str:
        if (
            container_name in service.containers
            or container_name in service.container_models
        ):
            return service.add_service_name(container_name)
        raise KeyError(
            "Container {} is not configured in service {}".format(
                container_name, service.name()
            )
        )

    def to_url(self, scheme: str, extractor_args: ExtractorArgs) -> Output[str]:
        root = self.root
        service = (
            extractor_args.host.services[root.service]
            if root.service
            else extractor_args.service
        )

        if root.external is not None:
            service_name = (
                GlobalExtractor(root.external).extract_str(extractor_args)
                if isinstance(root.external, GlobalExtract)
                else str(root.external)
            )
        else:
            network_config = service.container_models[root.container].network.root
            if isinstance(network_config, ContainerNetworkModeConfig):
                match network_config.mode:
                    case ContainerNetworkMode.HOST:
                        service_name = ContainerHostModeConfig.LOCALHOST_HOST
                    case ContainerNetworkMode.NONE:
                        raise ValueError(
                            "Could not route traffic to container with no network"
                        )
            elif isinstance(network_config, ContainerNetworkContainerConfig):
                service_name = self.get_service_name(
                    network_config.container,
                    extractor_args.services[network_config.service]
                    if network_config.service
                    else service,
                )
            else:
                service_name = self.get_service_name(root.container, service)

        return Output.format(
            "{}{}:{}",
            scheme,
            service_name,
            GlobalExtractor(root.port_)
            .extract_str(extractor_args)
            .apply(lambda x: TypeAdapter(PositiveInt).validate_python(int(x))),
        )

    def to_service(
        self,
        type_: TraefikDynamicType,
        router_name: str,
        extractor_args: ExtractorArgs,
    ) -> dict[str, Any]:
        root = self.root

        match type_:
            case TraefikDynamicType.HTTP:
                service_key = "url"
                scheme = (root.scheme or type_) + "://"
            case TraefikDynamicType.TCP:
                service_key = "address"
                scheme = ""

        return {
            router_name: {
                "loadBalancer": {
                    "servers": [{service_key: self.to_url(scheme, extractor_args)}]
                }
                | (
                    {"passHostHeader": root.pass_host_header}
                    if root.pass_host_header is not None
                    else {}
                )
            }
        }


class TraefikDynamicServiceModelBuilder(HomelabRootModel[TraefikDynamicServiceModel]):
    @property
    def full(self) -> TraefikDynamicServiceFullModel | None:
        root = self.root.root

        if isinstance(root, TraefikDynamicServiceFullModel):
            return root
        return None

    def to_service_name(self, router_name: str) -> str:
        root = self.root.root

        return (
            router_name
            if isinstance(root, (TraefikDynamicServiceFullModel, int))
            else root
        )
