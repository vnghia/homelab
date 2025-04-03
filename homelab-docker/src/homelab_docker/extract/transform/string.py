import re

from homelab_extract.transform.string import ExtractTransformString
from homelab_pydantic import HomelabRootModel


class ExtractStringTransformer(HomelabRootModel[ExtractTransformString]):
    def transform(self, value: str) -> str:
        root = self.root
        if root.capture:
            match = re.match(root.capture, value)
            assert match, "No match capture"
            value = match[1]
        if root.template:
            value = root.template.format(value=value)
        return value
