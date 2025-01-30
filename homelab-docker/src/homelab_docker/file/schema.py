from typing import Any

import httpx
import jsonschema


class Schema:
    def __init__(self, url: str) -> None:
        self.schema = httpx.get(url=url).raise_for_status().json()

    def validate(self, data: Any) -> None:
        jsonschema.validate(data, self.schema)
