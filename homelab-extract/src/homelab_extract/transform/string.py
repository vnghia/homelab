import re

from homelab_pydantic import HomelabBaseModel
from pydantic import TypeAdapter

CollectionAdapter: TypeAdapter[dict[str, str] | list[str]] = TypeAdapter(
    dict[str, str] | list[str]
)


class ExtractTransformString(HomelabBaseModel):
    capture: str | None = None
    template: str | None = None

    def transform(self, value: str, collection: bool) -> str:
        if self.capture:
            match = re.match(self.capture, value)
            if not match:
                raise ValueError("Could not extract value from {}".format(value))
            value = match[1]

        if self.template:
            value_data = self.parse(value, collection)
            format_args: dict[str, str] = {}
            if isinstance(value_data, dict):
                format_args |= value_data
            elif isinstance(value_data, list):
                for index, value in enumerate(value_data):
                    format_args["value" + str(index)] = value
            else:
                format_args["value"] = value
            value = self.template.format(**format_args)
        return value

    @classmethod
    def parse(cls, value: str, collection: bool) -> dict[str, str] | list[str] | str:
        return CollectionAdapter.validate_json(value) if collection else value
