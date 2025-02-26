from pathlib import PosixPath

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_network.resource.network import NetworkResource
from homelab_pydantic import RelativePath
from homelab_tailscale_service import TailscaleService
from pulumi import ResourceOptions

from .config import TraefikConfig
from .model.dynamic.http import TraefikDynamicHttpModel
from .model.dynamic.service import TraefikDynamicServiceModel
from .resource.static import TraefikStaticConfigResource


class TraefikService(ServiceWithConfigResourceBase[TraefikConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[TraefikConfig],
        *,
        opts: ResourceOptions | None,
        tailscale_service: TailscaleService,
        network_resource: NetworkResource,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)
        self.network_resource = network_resource

        self.static = TraefikStaticConfigResource(
            opts=self.child_opts,
            traefik_service=self,
            tailscale_service=tailscale_service,
        )

        self.build_containers(
            options={
                None: ContainerModelBuildArgs(
                    opts=ResourceOptions(delete_before_replace=True),
                    envs={
                        "CF_ZONE_API_TOKEN": network_resource.token.read.value,
                        "CF_DNS_API_TOKEN": network_resource.token.write.value,
                    },
                    files=[self.static],
                )
            }
        )

        TraefikDynamicHttpModel(
            name="dashboard",
            public=False,
            hostname="system",
            prefix=self.config.path,
            service=TraefikDynamicServiceModel("api@internal"),
        ).build_resource(
            None, opts=self.child_opts, main_service=self, traefik_service=self
        )

        self.register_outputs({})

    def get_dynamic_config_volume_path(self, name: str) -> ContainerVolumePath:
        return self.static.dynamic_directory_volume_path / RelativePath(PosixPath(name))
