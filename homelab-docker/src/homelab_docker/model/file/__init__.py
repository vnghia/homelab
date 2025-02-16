import hashlib
from typing import Any

import pulumi
from pydantic import (
    BaseModel,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
)

from homelab_docker.pydantic.path import RelativePath


class FileLocationModel(BaseModel):
    volume: str
    path: RelativePath

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())


class FileDataModel(BaseModel):
    content: str
    mode: int

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()

    @field_validator("content", mode="wrap")
    @classmethod
    def ignore_non_string_input(
        cls, data: Any, _: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> str:
        if isinstance(data, str):
            return data
        else:
            pulumi.log.warn(
                "Non string data encountered: {}. Validated data: {}".format(
                    data, info.data
                )
            )
            return "Unknown"
