from __future__ import annotations

import typing

from homelab_docker.extract import ExtractorArgs
from homelab_docker.resource.file.config import ConfigFileResource, YamlDumper
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
        dagu_service: DaguService,
        extractor_args: ExtractorArgs,
    ) -> None:
        self.model = model.root
        resource_name = resource_name or extractor_args.service.name()
        self.path = self.model.path or resource_name
        super().__init__(
            resource_name,
            opts=opts,
            volume_path=dagu_service.get_dag_volume_path(self.path),
            data=model.to_data(
                dagu_service,
                extractor_args,
                dagu_service.get_log_dir_volume_path(),
            ),
            extractor_args=dagu_service.extractor_args,
        )
