from typing import Any

import deepmerge
import httpx
import jsonschema


class Schema:
    def __init__(self, url: str, override: Any | None = None) -> None:
        self.schema = deepmerge.always_merger.merge(
            httpx.get(url=url).raise_for_status().json(), override or {}
        )

    def validate(self, data: Any) -> None:
        jsonschema.validate(data, self.schema)
