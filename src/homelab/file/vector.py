from homelab_docker.model.docker.container.network import (
    ContainerCommonNetworkConfig,
    ContainerNetworkModeConfig,
)
from homelab_docker.resource.service import ServiceResourceBase
from homelab_vector_service import VectorService
from homelab_vector_service.resource.enrichement import VectorEnrichmentTableResource
from pulumi import ComponentResource, ResourceOptions


class VectorFile(ComponentResource):
    RESOURCE_NAME = VectorService.name()

    def __init__(self, opts: ResourceOptions, vector_service: VectorService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)
        self.vector_service = vector_service

        self.container_network_modes: list[str] = ["alias,network_mode"]

    def build_one(self, service: ServiceResourceBase) -> None:
        service_opts = None
        for container, model in service.container_models.items():
            network_config = model.network.root
            if isinstance(network_config, ContainerCommonNetworkConfig):
                network_mode = "bridge"
            elif isinstance(network_config, ContainerNetworkModeConfig):
                network_mode = network_config.mode
            else:
                network_mode = "container:{}".format(
                    service.extractor_args.host.services[
                        network_config.service or service.name()
                    ].container_full_names[network_config.container]
                )
            self.container_network_modes.append(
                "{},{}".format(service.container_full_names[container], network_mode)
            )

            if not model.observability:
                continue
            if not service_opts:
                service_opts = ResourceOptions(
                    parent=ComponentResource(
                        service.name(), service.name(), None, opts=self.child_opts
                    )
                )
            self.vector_service.build_observability(
                opts=service_opts, service=service, container=container
            )

    def finalize(self) -> None:
        self.build_container_network_mode_enrichment()

    def build_container_network_mode_enrichment(self) -> None:
        self.container_network_mode_enrichment = VectorEnrichmentTableResource(
            "container-network-mode",
            opts=self.child_opts,
            content="\n".join(self.container_network_modes),
            schema={"alias": "string", "network_mode": "string"},
            vector_service=self.vector_service,
        )
