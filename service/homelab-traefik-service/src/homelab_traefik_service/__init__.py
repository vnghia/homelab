from collections import defaultdict
from pathlib import PosixPath

from homelab_docker.extract import ExtractorArgs
from homelab_docker.extract.global_ import GlobalExtractor
from homelab_docker.model.docker.container.volume_path import ContainerVolumePath
from homelab_docker.model.service import ServiceWithConfigModel
from homelab_docker.resource.service import (
    ServiceResourceBase,
    ServiceWithConfigResourceBase,
)
from homelab_network.resource.network import NetworkResource
from homelab_pydantic import RelativePath
from homelab_traefik_config import TraefikServiceConfig, TraefikServiceConfigBase
from homelab_traefik_config.model.dynamic.type import TraefikDynamicType
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
        extractor_args: ExtractorArgs,
    ) -> None:
        super().__init__(model, opts=opts, extractor_args=extractor_args)

        self.dynamic_directory_volume_path = GlobalExtractor(
            self.config.path.dynamic
        ).extract_volume_path(self.extractor_args)
        self.static = TraefikStaticConfigResource(
            opts=self.child_opts, traefik_service=self
        )

        self.acme_token = network_resource.token.acme_tokens[
            self.extractor_args.host.name
        ].value
        self.options[None].add_envs(
            {"CF_ZONE_API_TOKEN": self.acme_token, "CF_DNS_API_TOKEN": self.acme_token}
        )
        self.options[None].add_files([self.static])
        self.build_containers()

        self.routers: dict[
            str, dict[str | None, TraefikDynamicRouterConfigResource]
        ] = defaultdict(dict)
        self.middlewares: dict[
            str,
            dict[
                TraefikDynamicType,
                dict[str | None, TraefikDynamicMiddlwareConfigResource],
            ],
        ] = defaultdict(lambda: defaultdict(dict))

        self.register_outputs({})

    def get_dynamic_config_volume_path(self, name: str) -> ContainerVolumePath:
        return self.dynamic_directory_volume_path / RelativePath(PosixPath(name))

    @classmethod
    def get_service_config(
        cls, service: ServiceResourceBase
    ) -> TraefikServiceConfig | None:
        if (
            isinstance(service, ServiceWithConfigResourceBase)
            and isinstance(service.config, TraefikServiceConfigBase)
            and service.config.traefik
        ):
            return service.config.traefik
        return None
