from __future__ import annotations

import typing
from typing import Any

from homelab_extract.project import GlobalExtractProjectSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalProjectSourceExtractor(ExtractorBase[GlobalExtractProjectSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> dict[str, Any]:
        return {
            k.removeprefix("pulumi."): v
            for k, v in extractor_args.global_args.project.labels.items()
        }
