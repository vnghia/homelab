from __future__ import annotations

import typing

from homelab_extract.container.info import (
    ContainerExtractInfoSource,
    ContainerInfoSource,
)
from pulumi import Output

from .. import ExtractorBase

if typing.TYPE_CHECKING:
    from .. import ExtractorArgs


class ContainerInfoSourceExtractor(ExtractorBase[ContainerExtractInfoSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Output[str]:
        cinfo = self.root.cinfo
        match cinfo:
            case ContainerInfoSource.ID:
                return extractor_args.container.id
            case ContainerInfoSource.NAME:
                return extractor_args.container.name
