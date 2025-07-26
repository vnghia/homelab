from __future__ import annotations

import typing

from homelab_dagu_config.model.dotenv import DaguDagDotenvModel
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from homelab_pydantic import HomelabRootModel
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from .. import DaguService


class DaguDagDotenvModelBuilder(HomelabRootModel[DaguDagDotenvModel]):
    def build_resource(
        self,
        resource_name: str | None,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
    ) -> DotenvFileResource:
        resource = DotenvFileResource(
            resource_name or main_service.name(),
            opts=opts,
            volume_path=dagu_service.get_dotenv_volume_path(
                main_service.add_service_name(resource_name)
            ),
            envs=self.root.to_envs(main_service, None),
            volume_resource=main_service.docker_resource_args.volume,
        )
        dagu_service.dotenvs[main_service.name()][resource_name] = resource
        return resource
