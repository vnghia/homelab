import json
import re
import secrets
from typing import ClassVar

from homelab_pydantic import HomelabBaseModel


class ExtractTransformString(HomelabBaseModel):
    JSON_KEY: ClassVar[str] = "__json_key"
    JSON_VALUE: ClassVar[str] = secrets.token_hex(16)

    capture: str | None = None
    template: str | None = None

    def transform(self, value: str) -> str:
        if self.capture:
            match = re.match(self.capture, value)
            if not match:
                raise ValueError("Could not extract value from {}".format(value))
            value = match[1]

        if self.template:
            value_data = self.parse(value)
            format_args: dict[str, str] = {}
            if isinstance(value_data, dict):
                format_args |= value_data
            else:
                format_args["value"] = value
            value = self.template.format(**format_args)
        return value

    @classmethod
    def parse(cls, value: str) -> dict[str, str] | str:
        try:
            data = json.loads(value)
            if isinstance(data, dict) and data.get(cls.JSON_KEY) == cls.JSON_VALUE:
                return data
            return value
        except json.JSONDecodeError:
            return value
