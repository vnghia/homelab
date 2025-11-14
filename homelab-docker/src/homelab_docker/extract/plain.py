from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_extract.plain import GlobalPlainExtractSource
from homelab_pydantic import AbsolutePath

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalPlainSourceExtractor(ExtractorBase[GlobalPlainExtractSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        return self.root.extract_str(extractor_args.plain_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return AbsolutePath(PosixPath(self.extract_str(extractor_args)))
