from __future__ import annotations

from .base import SecretCertBaseModel


class SecretSelfSignedCertModel(SecretCertBaseModel):
    key: str | None
