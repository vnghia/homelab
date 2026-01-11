from __future__ import annotations

import typing
from typing import Any

import yaml_rs
from homelab_extract.include import GlobalExtractIncludeSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalIncludeSourceExtractor(ExtractorBase[GlobalExtractIncludeSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> Any | str:
        from .global_ import GlobalExtractor

        path = self.root.include.root
        with open(path, "rb") as file:
            match path.suffix:
                case ".yaml":
                    return GlobalExtractor.extract_recursively(
                        yaml_rs.load(file), extractor_args
                    )
                case _:
                    return file.read().decode()
