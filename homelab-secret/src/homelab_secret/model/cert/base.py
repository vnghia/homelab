from __future__ import annotations

from homelab_extract import GlobalExtract
from homelab_pydantic import HomelabBaseModel
from pydantic import PositiveInt

from .. import SecretModel


class SecretCertSubjectModel(HomelabBaseModel):
    common_name: GlobalExtract | None = None
    organizational_unit: GlobalExtract | None = None


class SecretCertBaseModel(SecretModel):
    allowed_uses: list[str] = ["any_extended"]
    validity_period_hours: PositiveInt = 100 * 365 * 24  # 100 years
    is_ca_certificate: bool | None = None
    subject: SecretCertSubjectModel | None = None
