import re

from homelab_pydantic import HomelabBaseModel, HomelabRootModel
from pydantic import TypeAdapter

CollectionAdapter: TypeAdapter[dict[str, str] | list[str]] = TypeAdapter(
    dict[str, str] | list[str]
)


class ExtractTransformStringJoinTemplate(HomelabBaseModel):
    join: str


class ExtractTransformStringTemplate(
    HomelabRootModel[str | ExtractTransformStringJoinTemplate]
):
    pass


class ExtractTransformString(HomelabBaseModel):
    capture: str | None = None
    template: ExtractTransformStringTemplate | None = None

    def transform(self, value: str, collection: bool) -> str:
        if self.capture:
            match = re.match(self.capture, value)
            if not match:
                raise ValueError("Could not extract value from {}".format(value))
            value = match[1]

        if self.template:
            template = self.template.root
            value_data = self.parse(value, collection)

            if isinstance(template, str):
                format_args: dict[str, str] = {}
                if isinstance(value_data, dict):
                    format_args |= value_data
                elif isinstance(value_data, list):
                    for index, value in enumerate(value_data):
                        format_args["value" + str(index)] = value
                else:
                    format_args["value"] = value
                value = template.format(**format_args)
            else:
                join_args: list[str] = []
                if isinstance(value_data, dict):
                    join_args += [
                        value[1]
                        for value in sorted(value_data.items(), key=lambda x: x[0])
                    ]
                elif isinstance(value_data, list):
                    join_args += value_data
                else:
                    join_args.append(value)
                value = template.join.join(join_args)
        return value

    @classmethod
    def parse(cls, value: str, collection: bool) -> dict[str, str] | list[str] | str:
        return CollectionAdapter.validate_json(value) if collection else value
