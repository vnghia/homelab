from __future__ import annotations

import typing

from homelab_extract.container.id import ContainerExtractIdSource
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ContainerIdSourceExtractor(ExtractorBase[ContainerExtractIdSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        return extractor_args.container.id
