from __future__ import annotations

from pydantic import PositiveInt

from .. import SecretModel


class SecretCertBaseModel(SecretModel):
    allowed_uses: list[str] = ["any_extended"]
    validity_period_hours: PositiveInt = 100 * 365 * 24  # 100 years
