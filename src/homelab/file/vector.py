from homelab_docker.resource.service import ServiceResourceBase
from homelab_vector_service import VectorService
from pulumi import ComponentResource, ResourceOptions


class VectorFile(ComponentResource):
    RESOURCE_NAME = VectorService.name()

    def __init__(self, opts: ResourceOptions, vector_service: VectorService) -> None:
        super().__init__(self.RESOURCE_NAME, self.RESOURCE_NAME, None, opts=opts)
        self.child_opts = ResourceOptions(parent=self)
        self.vector_service = vector_service

    def build_one(self, service: ServiceResourceBase) -> None:
        service_opts = None
        for container, resource in service.containers.items():
            if not resource.model.observability:
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
