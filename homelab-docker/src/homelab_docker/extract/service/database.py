from __future__ import annotations

import typing

from homelab_extract.service.database import ServiceExtractDatabaseSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ServiceDatabaseSourceExtractor(ExtractorBase[ServiceExtractDatabaseSource]):
    def extract_str(
        self, extractor_args: ExtractorArgs
    ) -> Output[str] | dict[str, Output[str]]:
        from ...model.database.type import DatabaseType

        root = self.root
        type = DatabaseType(root.type)
        version = (
            root.version
            or extractor_args.docker_resource_args.config.database.root[type].version
        )
        source = extractor_args.service.database.source_config[type][root.database][
            version
        ][0]
        database = root.database or source.database

        result: dict[str, Output[str]] = (
            {
                "username": Output.from_input(source.username),
                "password": Output.from_input(source.password),
                "host": Output.from_input(source.host),
                "port": Output.from_input(source.port).apply(str),
            }
            | ({"database": Output.from_input(database)} if database else {})
            | ({"url": source.to_url(root.scheme)} if root.scheme else {})
        )

        if root.info:
            info = root.info
            if not isinstance(info, list):
                return result[str(info)]
            return {str(k): result[str(k)] for k in info}
        return result
