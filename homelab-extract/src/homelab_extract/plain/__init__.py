from __future__ import annotations

import dataclasses
from typing import Self

from homelab_pydantic import HomelabRootModel, Hostnames
from homelab_s3 import S3Config

from .hostname import GlobalPlainExtractHostnameSource
from .type import GlobalPlainExtractTypeSource


@dataclasses.dataclass
class PlainArgs:
    s3: S3Config
    hostnames: Hostnames
    host: str | None

    def with_host(self, host: str | None) -> PlainArgs:
        return self.__replace__(host=host)


class GlobalPlainExtractSource(
    HomelabRootModel[GlobalPlainExtractHostnameSource | GlobalPlainExtractTypeSource]
):
    def extract_str(self, plain_args: PlainArgs) -> str:
        return self.root.extract_str(plain_args)

    @classmethod
    def from_simple(cls, value: str) -> Self:
        return cls(GlobalPlainExtractTypeSource(value))
