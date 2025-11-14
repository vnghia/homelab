import dataclasses
from typing import Self

from homelab_pydantic import HomelabRootModel, Hostnames

from .hostname import GlobalPlainExtractHostnameSource
from .type import GlobalPlainExtractTypeSource


@dataclasses.dataclass
class PlainArgs:
    hostnames: Hostnames
    host: str | None


class GlobalPlainExtractSource(
    HomelabRootModel[GlobalPlainExtractHostnameSource | GlobalPlainExtractTypeSource]
):
    def extract_str(self, plain_args: PlainArgs) -> str:
        return self.root.extract_str(plain_args)

    @classmethod
    def from_simple(cls, value: str) -> Self:
        return cls(GlobalPlainExtractTypeSource(value))
