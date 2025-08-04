from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_extract.simple import GlobalExtractSimpleSource
from homelab_pydantic import AbsolutePath

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalSimpleSourceExtractor(ExtractorBase[GlobalExtractSimpleSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        root = self.root.root
        if isinstance(root, bool):
            return str(root).lower()
        return str(root)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        return AbsolutePath(PosixPath(self.extract_str(extractor_args)))
