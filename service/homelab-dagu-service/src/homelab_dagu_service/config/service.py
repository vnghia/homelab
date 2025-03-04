from __future__ import annotations

from homelab_dagu_config import DaguServiceConfig
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

from .. import DaguService


class DaguServiceConfigBuilder(HomelabRootModel[DaguServiceConfig]):
    def build_resources(
        self,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
    ) -> dict[str | None, None]:
        root = self.root
        return {}
