from homelab_docker.extract import ExtractorArgs
from homelab_pydantic.model import HomelabRootModel
from homelab_traefik_config import TraefikServiceConfig
from homelab_traefik_config.model.dynamic import TraefikDynamicModel
from homelab_traefik_config.model.dynamic.middleware import (
    TraefikDynamicMiddlewareBuildModel,
)
from pulumi import ResourceOptions

from .. import TraefikService
from ..model.dynamic import TraefikDynamicModelBuilder
from ..resource.dynamic import TraefikDynamicConfigResource


class TraefikServiceConfigBuilder(HomelabRootModel[TraefikServiceConfig]):
    def build_resources(
        self,
        *,
        opts: ResourceOptions,
        traefik_service: TraefikService,
        extractor_args: ExtractorArgs,
    ) -> dict[str | None, TraefikDynamicConfigResource]:
        root = self.root.dynamic.root
        service = extractor_args.service

        if service.model.ondemand:
            more: dict[str | None, TraefikDynamicModel] = {
                traefik_service.ONDEMAND_NAME: TraefikDynamicModel(
                    TraefikDynamicMiddlewareBuildModel(
                        name=traefik_service.ONDEMAND_NAME,
                        data={
                            "sablierUrl": traefik_service.config.sablier_.url.model_dump(
                                mode="json"
                            ),
                            "group": service.name(),
                            "dynamic": {"displayName": service.name()},
                        },
                        plugin=traefik_service.ONDEMAND_NAME,
                    )
                )
            }
            root = more | root

        configs = {}
        for name, model in root.items():
            if model.active:
                configs[name] = TraefikDynamicModelBuilder(model).build_resource(
                    name,
                    opts=opts,
                    traefik_service=traefik_service,
                    extractor_args=extractor_args,
                )

        return configs
