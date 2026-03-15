from homelab_pydantic import HomelabRootModel

from ..model.b2 import B2BucketModel


class B2BucketConfig(HomelabRootModel[dict[str, B2BucketModel]]):
    root: dict[str, B2BucketModel] = {}

    def __getitem__(self, key: str) -> B2BucketModel:
        return self.root[key]
