from __future__ import annotations

import typing

from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
from homelab_docker.resource.service import ServiceResourceBase
from pulumi import ResourceOptions

from ..model import DaguDagModelBuilder
from . import schema

if typing.TYPE_CHECKING:
    from .. import DaguService


class DaguDagResource(ConfigFileResource[schema.Model], module="dagu", name="Dag"):
    validator = schema.Model
    dumper = YamlDumper[schema.Model]

    def __init__(
        self,
        resource_name: str | None,
        model: DaguDagModelBuilder,
        *,
        opts: ResourceOptions,
        main_service: ServiceResourceBase,
        dagu_service: DaguService,
    ) -> None:
        self.model = model.root
        resource_name = resource_name or main_service.name()
        self.path = self.model.path or resource_name
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=dagu_service.get_dag_volume_path(self.path),
            data=model.to_data(
                main_service,
                dagu_service,
                dagu_service.get_log_dir_volume_path(self.path),
            ),
            volume_resource=dagu_service.docker_resource_args.volume,
        )
