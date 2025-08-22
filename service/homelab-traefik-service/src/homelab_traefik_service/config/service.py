from homelab_docker.extract import ExtractorArgs
from homelab_pydantic.model import HomelabRootModel
from homelab_traefik_config import TraefikServiceConfig
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
        root = self.root.root

        return {
            name: TraefikDynamicModelBuilder(model).build_resource(
                name,
                opts=opts,
                traefik_service=traefik_service,
                extractor_args=extractor_args,
            )
            for name, model in root.items()
            if model.active
        }
