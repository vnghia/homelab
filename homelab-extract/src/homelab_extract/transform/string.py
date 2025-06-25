import re

from homelab_pydantic import HomelabBaseModel


class ExtractTransformString(HomelabBaseModel):
    capture: str | None = None
    template: str | None = None

    def transform(self, value: str) -> str:
        from homelab_docker.extract.kv import GlobalKvSourceExtractor

        if self.capture:
            match = re.match(self.capture, value)
            if not match:
                raise ValueError("Could not extract value from {}".format(value))
            value = match[1]

        if self.template:
            value_data = GlobalKvSourceExtractor.parse(value)
            format_args: dict[str, str] = {}
            if isinstance(value_data, dict):
                format_args |= value_data
            else:
                format_args["value"] = value
            value = self.template.format(**format_args)
        return value
