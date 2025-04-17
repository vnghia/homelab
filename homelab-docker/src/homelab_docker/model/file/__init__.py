import hashlib
from typing import Any

import pulumi
from homelab_pydantic import HomelabBaseModel, RelativePath
from pydantic import ValidationInfo, ValidatorFunctionWrapHandler, field_validator


class FileLocationModel(HomelabBaseModel):
    volume: str
    path: RelativePath

    @property
    def id_(self) -> str:
        return "{}:{}".format(self.volume, self.path.as_posix())


class FileDataModel(HomelabBaseModel):
    content: str
    mode: int

    @property
    def hash(self) -> str:
        return hashlib.sha256(self.content.encode()).hexdigest()

    @field_validator("content", mode="wrap")
    @classmethod
    def ignore_pulumi_unknown(
        cls, data: Any, handler: ValidatorFunctionWrapHandler, info: ValidationInfo
    ) -> str:
        if isinstance(data, pulumi.output.Unknown):
            pulumi.log.warn(
                "Pulumi unknown output encountered: {}. Validated data: {}".format(
                    data, info.data
                )
            )
            return ""
        return handler(data)  # type: ignore[no-any-return]
