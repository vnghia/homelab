from typing import Self

from homelab_pydantic import HomelabRootModel

from .model import SecretModel


class SecretConfig(HomelabRootModel[dict[str, SecretModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})
