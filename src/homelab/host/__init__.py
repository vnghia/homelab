from homelab_docker.config import DockerServiceModelConfigs
from homelab_docker.config.service import ServiceConfigBase
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.host import HostResourceBase
from homelab_extra_service import ExtraService
from homelab_extra_service.config import ExtraConfig
from homelab_network.resource.network import NetworkResource
from pulumi import ResourceOptions
from pydantic.alias_generators import to_snake


class HostBase[T: ServiceConfigBase](HostResourceBase):
    def __init__(
        self,
        config: T,
        *,
        opts: ResourceOptions | None,
        project_prefix: str,
        project_labels: dict[str, str],
        network_resource: NetworkResource,
        docker_service_model_configs: DockerServiceModelConfigs,
    ) -> None:
        super().__init__(
            opts=opts,
            project_prefix=project_prefix,
            project_labels=project_labels,
            network_resource=network_resource,
            docker_service_model_configs=docker_service_model_configs,
        )

        self.services_config = config

    def build_extra_services(self) -> None:
        self.extra_services = {
            service: type(
                "{}Service".format(service.capitalize()), (ExtraService,), {}
            )(model, opts=self.child_opts, extractor_args=self.extractor_args).build()
            for service, model in ExtraService.sort_depends_on(
                self.services_config.extra(ServiceWithConfigModel[ExtraConfig])
            ).items()
        }

    @classmethod
    def name(cls) -> str:
        return to_snake(cls.__name__.removesuffix("Host")).replace("_", "-")
