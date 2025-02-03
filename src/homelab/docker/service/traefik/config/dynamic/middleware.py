from typing import Any

from pydantic import BaseModel, ConfigDict


class Middleware(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    data: Any
