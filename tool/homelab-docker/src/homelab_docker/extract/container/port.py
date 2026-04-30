from __future__ import annotations

import typing

from homelab_extract import GlobalExtract
from homelab_extract.container.port import (
    ContainerExtractPortSource,
    ContainerPortSource,
)
from pulumi import Output
from pydantic import PositiveInt

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ContainerPortSourceExtractor(ExtractorBase[ContainerExtractPortSource]):
    @classmethod
    def extract_port(
        cls, port: PositiveInt | GlobalExtract, extractor_args: ExtractorArgs
    ) -> Output[str]:
        from ...extract.global_ import GlobalExtractor

        if isinstance(port, int):
            return Output.from_input(str(port))
        return GlobalExtractor(port).extract_str(extractor_args)

    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        root = self.root
        port = extractor_args.container_model.ports.root[root.port]
        match root.info:
            case ContainerPortSource.INTERNAL:
                if not port.internal:
                    raise ValueError("Internal port is not configured")
                return self.extract_port(port.internal, extractor_args)
            case ContainerPortSource.EXTERNAL:
                if not port.external:
                    if not port.internal:
                        raise ValueError(
                            "Neither external or internal port is configured"
                        )
                    return self.extract_port(port.internal, extractor_args)
                return self.extract_port(port.external, extractor_args)
