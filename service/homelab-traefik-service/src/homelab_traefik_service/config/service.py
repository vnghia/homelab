from homelab_docker.resource.service import ServiceResourceBase
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
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        traefik_service: TraefikService,
    ) -> dict[str | None, TraefikDynamicConfigResource]:
        root = self.root.root

        return {
            name: TraefikDynamicModelBuilder(model).build_resource(
                name,
                opts=opts,
                main_service=main_service,
                traefik_service=traefik_service,
            )
            for name, model in root.items()
        }
