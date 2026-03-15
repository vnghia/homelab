from __future__ import annotations

import typing
from pathlib import PosixPath

from homelab_extract.plain import GlobalPlainExtractSource
from homelab_pydantic import AbsolutePath
from pulumi import Output

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalPlainSourceExtractor(ExtractorBase[GlobalPlainExtractSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str | Output[str]:
        return self.root.extract_str(extractor_args.plain_args)

    def extract_path(self, extractor_args: ExtractorArgs) -> AbsolutePath:
        result = self.extract_str(extractor_args)
        if not isinstance(result, str):
            raise TypeError("Could not extract path from {}".format(self.name))
        return AbsolutePath(PosixPath(result))
