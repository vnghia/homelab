from __future__ import annotations

import typing

from homelab_extract.container.port import (
    ContainerExtractPortSource,
    ContainerPortSource,
)

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ContainerPortSourceExtractor(ExtractorBase[ContainerExtractPortSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        root = self.root
        port = extractor_args.container_model.ports[root.port]
        match root.info:
            case ContainerPortSource.INTERNAL:
                if not port.internal:
                    raise ValueError("Internal port is not configured")
                return str(port.internal)
            case ContainerPortSource.EXTERNAL:
                if not port.external:
                    if not port.internal:
                        raise ValueError(
                            "Nor external or internal port is not configured"
                        )
                    return str(port.internal)
                return str(port.external)
