from __future__ import annotations

import dataclasses
from typing import Self

from homelab_mail.resource import MailCredentials
from homelab_pydantic import HomelabRootModel, Hostnames
from homelab_s3.resource import S3Credentials
from pulumi import Output

from .hostname import GlobalPlainExtractHostnameSource
from .s3 import GlobalPlainExtractS3Source
from .type import GlobalPlainExtractTypeSource


@dataclasses.dataclass
class PlainArgs:
    mail: MailCredentials
    s3: S3Credentials
    hostnames: Hostnames
    host: str | None

    def with_host(self, host: str | None) -> PlainArgs:
        return self.__replace__(host=host)


class GlobalPlainExtractSource(
    HomelabRootModel[
        GlobalPlainExtractHostnameSource
        | GlobalPlainExtractS3Source
        | GlobalPlainExtractTypeSource
    ]
):
    def extract_str(self, plain_args: PlainArgs) -> str | Output[str]:
        return self.root.extract_str(plain_args)

    @classmethod
    def from_simple(cls, value: str) -> Self:
        return cls(GlobalPlainExtractTypeSource(value))
