from __future__ import annotations

from typing import Self

from homelab_pydantic import HomelabBaseModel, HomelabRootModel

from .config import GlobalExtractConfigSource
from .context import GlobalExtractContextSource
from .dict_ import GlobalExtractDictSource
from .host import HostExtract
from .include import GlobalExtractIncludeSource
from .kv import GlobalExtractKvSource
from .list_ import GlobalExtractListSource
from .plain import GlobalPlainExtractSource
from .project import GlobalExtractProjectSource
from .secret import GlobalExtractSecretSource
from .transform import ExtractTransform
from .variable import GlobalExtractVariableSource


class GlobalExtractSource(
    HomelabRootModel[
        GlobalExtractConfigSource
        | GlobalExtractContextSource
        | GlobalExtractDictSource
        | GlobalExtractIncludeSource
        | GlobalExtractKvSource
        | GlobalExtractListSource
        | GlobalPlainExtractSource
        | GlobalExtractProjectSource
        | GlobalExtractSecretSource
        | GlobalExtractVariableSource
    ]
):
    pass


class GlobalExtractFull(HomelabBaseModel):
    host: str | None = None
    extract: HostExtract | GlobalExtractSource
    transform: ExtractTransform | None = ExtractTransform()


class GlobalExtract(
    HomelabRootModel[GlobalExtractFull | GlobalExtractSource | HostExtract]
):
    @classmethod
    def from_simple(cls, value: str) -> Self:
        return cls(GlobalExtractSource(GlobalPlainExtractSource.from_simple(value)))

    def to_full(self) -> GlobalExtractFull:
        root = self.root
        if isinstance(root, GlobalExtractFull):
            return root
        return GlobalExtractFull(extract=root)

    def with_service(self, service: str, force: bool) -> Self:
        full = self.to_full()
        if isinstance(full.extract, HostExtract):
            full = full.__replace__(extract=full.extract.with_service(service, force))
        return self.model_construct(full)

    @classmethod
    def with_service_nullable(
        cls, extract: GlobalExtract | None, service: str, force: bool
    ) -> GlobalExtract | None:
        if isinstance(extract, GlobalExtract):
            return extract.with_service(service, force)
        return extract


GlobalExtractSource.model_rebuild()
GlobalExtractFull.model_rebuild()
GlobalExtract.model_rebuild()
