from __future__ import annotations

from typing import Literal, overload

import pulumi_tls as tls
from homelab_extract.plain import GlobalPlainExtractSource, PlainArgs
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from ..base import SecretBaseModel


class SecretCertSubjectModel(HomelabBaseModel):
    common_name: GlobalPlainExtractSource | None = None
    organizational_unit: GlobalPlainExtractSource | None = None

    @overload
    def to_args(
        self, is_cert_request: Literal[True], plain_args: PlainArgs
    ) -> tls.CertRequestSubjectArgs: ...

    @overload
    def to_args(
        self, is_cert_request: Literal[False], plain_args: PlainArgs
    ) -> tls.SelfSignedCertSubjectArgs: ...

    def to_args(
        self, is_cert_request: bool, plain_args: PlainArgs
    ) -> tls.CertRequestSubjectArgs | tls.SelfSignedCertSubjectArgs:
        return (
            tls.CertRequestSubjectArgs
            if is_cert_request
            else tls.SelfSignedCertSubjectArgs
        )(
            common_name=self.common_name.extract_str(plain_args)
            if self.common_name
            else None,
            organizational_unit=self.organizational_unit.extract_str(plain_args)
            if self.organizational_unit
            else None,
        )


class SecretCertBaseModel(SecretBaseModel):
    allowed_uses: list[str] = ["any_extended"]
    validity_period_hours: PositiveInt = 100 * 365 * 24  # 100 years
    is_ca_certificate: bool | None = None
    dns: list[GlobalPlainExtractSource] | None = None
    subject: SecretCertSubjectModel | None = None
