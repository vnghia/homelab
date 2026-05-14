from typing import Self

from homelab_pydantic import HomelabRootModel

from ..model.credential import S3CredentialModel


class S3CredentialConfig(HomelabRootModel[dict[str, S3CredentialModel]]):
    @classmethod
    def default(cls) -> Self:
        return cls({})

    def __getitem__(self, key: str) -> S3CredentialModel:
        return self.root[key]
