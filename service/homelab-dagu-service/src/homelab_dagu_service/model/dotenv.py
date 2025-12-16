from __future__ import annotations

import typing

from homelab_dagu_config.model.dotenv import DaguDagDotenvModel
from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.dotenv import DotenvFileResource
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
        extractor_args: ExtractorArgs,
        dagu_service: DaguService,
    ) -> DotenvFileResource:
        service = extractor_args.service
        resource = DotenvFileResource(
            resource_name or extractor_args.service.name(),
            opts=opts,
            volume_path=dagu_service.get_dotenv_volume_path(
                extractor_args.service.add_service_name(resource_name)
            ),
            envs=self.root.to_envs(extractor_args),
            permission=dagu_service.user,
            extractor_args=extractor_args,
        )
        dagu_service.dotenvs[service.name()][resource_name] = resource
        return resource
