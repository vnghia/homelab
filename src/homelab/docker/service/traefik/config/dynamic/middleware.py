from typing import Any

from pydantic import BaseModel


class TraefikMiddleware(BaseModel):
    name: str
    data: Any
