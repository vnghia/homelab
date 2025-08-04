from __future__ import annotations

import typing

from homelab_extract.docker import GlobalExtractDockerSource

from . import ExtractorBase

if typing.TYPE_CHECKING:
    from . import ExtractorArgs


class GlobalDockerSourceExtractor(ExtractorBase[GlobalExtractDockerSource]):
    def extract_str(self, extractor_args: ExtractorArgs) -> str:
        root = self.root
        return root.docker.format(
            timezone=extractor_args.docker_resource_args.timezone,
            **{
                k.removeprefix("pulumi."): v
                for k, v in extractor_args.docker_resource_args.project_labels.items()
            },
        )
