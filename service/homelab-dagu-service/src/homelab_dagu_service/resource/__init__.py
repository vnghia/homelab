from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from homelab_docker.resource.file.dotenv import DotenvFileResource
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from ..model import DaguDagModelBuilder
from . import schema

if typing.TYPE_CHECKING:
    from .. import DaguService


class DaguDagResource(ConfigFileResource[schema.Model], module="dagu", name="Dag"):
    validator = schema.Model
    dumper = YamlDumper

    def __init__(
        self,
        resource_name: str,
        model: DaguDagModelBuilder,
        *,
        opts: ResourceOptions | None,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
        dotenvs: list[DotenvFileResource] | None,
    ):
        self.model = model.root
        self.path = self.model.path or resource_name
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=dagu_service.get_dag_volume_path(self.path),
            data=model.to_data(
                main_service,
                dagu_service,
                dagu_service.get_log_dir_volume_path(self.path),
                dotenvs,
            ),
            volume_resource=dagu_service.docker_resource_args.volume,
        )
