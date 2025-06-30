import re

from homelab_pydantic import HomelabBaseModel
from homelab_pydantic.model import HomelabRootModel


class ExtractTransformString(HomelabBaseModel):
    capture: str | None = None
    template: str | None = None

    def transform(self, value: str, dictionary: bool) -> str:
        if self.capture:
            match = re.match(self.capture, value)
            if not match:
                raise ValueError("Could not extract value from {}".format(value))
            value = match[1]

        if self.template:
            value_data = self.parse(value, dictionary)
            format_args: dict[str, str] = {}
            if isinstance(value_data, dict):
                format_args |= value_data
            else:
                format_args["value"] = value
            value = self.template.format(**format_args)
        return value

    @classmethod
    def parse(cls, value: str, dictionary: bool) -> dict[str, str] | str:
        return (
            HomelabRootModel[dict[str, str]].model_validate_json(value).root
            if dictionary
            else value
        )
