from __future__ import annotations

import typing

from homelab_docker.model.container import ContainerModelBuildArgs
from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from homelab_dagu_service import DaguService

from ..model import DaguDagModel
from . import schema

if typing.TYPE_CHECKING:
    from .. import DaguService


class DaguDagResource(ConfigFileResource[schema.Model], module="dagu", name="Dag"):
    validator = schema.Model
    dumper = YamlDumper

    def __init__[T](
        self,
        resource_name: str,
        model: DaguDagModel,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase[T],
        dagu_service: DaguService,
        build_args: ContainerModelBuildArgs | None,
        dotenv: DotenvFileResource | None,
    ):
        super().__init__(
            resource_name,
            opts=opts,
            container_volume_path=dagu_service.get_dag_container_volume_path(
                model.path or resource_name
            ),
            data=model.to_data(main_service, dagu_service, build_args, dotenv),
            volume_resource=dagu_service.docker_resource_args.volume,
        )
