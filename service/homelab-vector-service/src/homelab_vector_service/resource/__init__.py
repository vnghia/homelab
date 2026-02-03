from __future__ import annotations

import dataclasses
import typing
from typing import Any

from homelab_docker.resource.file.config import (
    ConfigFileResource,
    JsonDefaultModel,
    TomlDumper,
)
from pulumi import ResourceOptions

if typing.TYPE_CHECKING:
    from .. import VectorService


@dataclasses.dataclass
class VectorConfigData:
    keys: dict[str, str]
    sources: dict[str, Any]
    transforms: dict[str, Any]
    sinks: dict[str, Any]
    enrichment_tables: dict[str, Any]


class VectorConfigResource(
    ConfigFileResource[JsonDefaultModel], module="vector", name="Config"
):
    validator = JsonDefaultModel
    dumper = TomlDumper[JsonDefaultModel]

    def __init__(
        self,
        resource_name: str,
        *,
        opts: ResourceOptions,
        config_data: VectorConfigData,
        vector_service: VectorService,
    ) -> None:
        self.path = resource_name
        self.keys = config_data.keys

        data = (
            ({"sources": config_data.sources} if config_data.sources else {})
            | ({"transforms": config_data.transforms} if config_data.transforms else {})
            | ({"sinks": config_data.sinks} if config_data.sinks else {})
            | (
                {"enrichment_tables": config_data.enrichment_tables}
                if config_data.enrichment_tables
                else {}
            )
        )

        super().__init__(
            resource_name,
            opts=opts,
            volume_path=vector_service.get_config_path(resource_name),
            data=data,
            permission=vector_service.user,
            extractor_args=vector_service.extractor_args,
        )
