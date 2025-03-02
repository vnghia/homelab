import re

from homelab_pydantic import HomelabBaseModel


class ExtractTransformString(HomelabBaseModel):
    capture: str | None = None
    template: str | None = None

    def transform(self, value: str) -> str:
        if self.capture:
            match = re.match(self.capture, value)
            assert match, "No match capture"
            value = match[1]
        if self.template:
            value = self.template.format(value=value)
        return value
