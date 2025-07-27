from collections import defaultdict
from pathlib import PosixPath

from homelab_docker.extract.service import ServiceExtractor
from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.model.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource import DockerResourceArgs
from homelab_docker.resource.service import ServiceWithConfigResourceBase
from homelab_network.resource.network import NetworkResource
from homelab_pydantic import RelativePath
from pulumi import ResourceOptions

from .config import TraefikConfig
from .resource.dynamic.middleware import TraefikDynamicMiddlwareConfigResource
from .resource.dynamic.router import TraefikDynamicRouterConfigResource
from .resource.static import TraefikStaticConfigResource


class TraefikService(ServiceWithConfigResourceBase[TraefikConfig]):
    def __init__(
        self,
        model: ServiceWithConfigModel[TraefikConfig],
        *,
        opts: ResourceOptions,
        network_resource: NetworkResource,
        docker_resource_args: DockerResourceArgs,
    ) -> None:
        super().__init__(model, opts=opts, docker_resource_args=docker_resource_args)

        self.dynamic_directory_volume_path = ServiceExtractor(
            self.config.path.dynamic
        ).extract_volume_path(self, None)
        self.static = TraefikStaticConfigResource(
            opts=self.child_opts,
            traefik_service=self,
            port=network_resource.config.port,
        )

        self.options[None] = ContainerModelBuildArgs(
            opts=ResourceOptions(delete_before_replace=True),
            envs={
                "CF_ZONE_API_TOKEN": network_resource.token.amce_tokens[
                    docker_resource_args.host
                ][0].value,
                "CF_DNS_API_TOKEN": network_resource.token.amce_tokens[
                    docker_resource_args.host
                ][1].value,
            },
            files=[self.static],
        )
        self.build_containers()

        self.routers: dict[
            str, dict[str | None, TraefikDynamicRouterConfigResource]
        ] = defaultdict(dict)
        self.middlewares: dict[
            str, dict[str | None, TraefikDynamicMiddlwareConfigResource]
        ] = defaultdict(dict)

        self.register_outputs({})

    def get_dynamic_config_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dynamic_directory_volume_path / RelativePath(PosixPath(name))
