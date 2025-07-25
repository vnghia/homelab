from homelab_extract.transform.string import ExtractTransformString
from homelab_pydantic import HomelabRootModel


class ExtractStringTransformer(HomelabRootModel[ExtractTransformString]):
    def transform(self, value: str, dictionary: bool) -> str:
        return self.root.transform(value, dictionary)
